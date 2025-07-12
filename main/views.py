from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password

from .db import (
    questions_col,
    users_col,
    user_activity_col,
    get_next_user_id,
    get_or_create_activity,
)
from types import SimpleNamespace

def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        confirmation_password = request.POST['confirmation_password']
        role = request.POST['role']
        school = request.POST['school']

        # Check if passwords match
        if password != confirmation_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if user already exists in the users collection
        if users_col.find_one({'email': email}):
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Hash the password before storing
        hashed_password = make_password(password)

        # Insert the user document into MongoDB
        users_col.insert_one({
            'user_id': get_next_user_id(),
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': role,
            'school': school
        })
        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'register.html')

def logout_view(request):
    """Log out the user."""
    if 'user_name' not in request.session:
        messages.error(request, "You are not logged in.")
        return redirect('login')
    
    try:
        request.session.flush()  # Clear all session data
        messages.success(request, "You have been logged out.")
    except Exception as e:
        messages.error(request, f"An error occurred during logout: {str(e)}")
    
    return redirect('login')
def home(request):
    """Render the home page with the question count from MongoDB."""
    total_questions = questions_col.count_documents({})
    return render(request, 'home.html', {'total_questions': total_questions})

def login_view(request):
    """Handle login using the users collection."""
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = users_col.find_one({'email': email})
        if user and check_password(password, user.get('password', '')):
            request.session['user_name'] = user['name']
            messages.success(request, f"Welcome back, {user['name']}!")
            return redirect('home')
        messages.error(request, "Invalid email or password.")
        return redirect('login')

    return render(request, 'login.html')
def question_bank(request):
    """Render the initial page with session codes."""
    session_codes = questions_col.distinct('session_code')
    return render(request, 'question_bank.html', {'session_codes': session_codes})

def get_subtopics(request):
    """Return subtopics for a given session code."""
    session_code = request.GET.get('session_code')
    if not session_code:
        return JsonResponse({'error': 'Session code is required'}, status=400)

    subtopics = questions_col.distinct('subtopic', {'session_code': session_code})
    if not subtopics:
        return JsonResponse({'error': 'No subtopics found for this session code'}, status=404)

    return JsonResponse({'subtopics': list(subtopics)})

import random

def practice_questions(request):
    """Render the practice questions page with questions in random order."""
    session_code = request.GET.get('session_code')
    subtopic = request.GET.get('subtopic')

    if not session_code or not subtopic:
        return render(request, 'error.html', {'message': 'Session code and subtopic are required'})

    # Fetch questions from MongoDB matching the filters
    docs = list(questions_col.find({'session_code': session_code, 'subtopic': subtopic}))
    random.shuffle(docs)
    # Convert dicts to simple objects for template compatibility
    questions = [SimpleNamespace(**doc) for doc in docs]
    return render(request, 'practice_questions.html', {'questions': questions})

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime

@csrf_exempt
def check_answer(request):
    question_id = request.POST.get('question_id')
    selected_answer = request.POST.get('selected_answer')
    doc = questions_col.find_one({'question_id': question_id})
    is_correct = doc and doc.get('answer') == selected_answer
    return JsonResponse({'is_correct': is_correct})


@csrf_exempt
@require_POST
def update_activity(request):
    """Update or record user activity for a question."""
    if 'user_name' not in request.session:
        return JsonResponse({'error': 'Authentication required'}, status=403)

    question_id = request.POST.get('question_id')
    action = request.POST.get('action')
    if not question_id or not action:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    user = users_col.find_one({'name': request.session['user_name']})
    if not user:
        return JsonResponse({'error': 'User not found'}, status=404)

    activity = get_or_create_activity(user['user_id'], question_id)
    updates = {}

    if action == 'start':
        updates['time_started'] = datetime.utcnow()
        user_activity_col.update_one({'_id': activity['_id']}, {
            '$set': updates,
            '$inc': {'times_viewed': 1},
        })
    elif action == 'answer':
        correct = request.POST.get('correct') == 'true'
        time_took = None
        if activity.get('time_started'):
            time_took = datetime.utcnow() - activity['time_started']
            updates['time_took'] = time_took
        updates.update({'solved': True, 'correct': correct})
        user_activity_col.update_one({'_id': activity['_id']}, {'$set': updates})
    elif action == 'bookmark':
        new_state = not activity.get('bookmarked', False)
        updates['bookmarked'] = new_state
        user_activity_col.update_one({'_id': activity['_id']}, {'$set': updates})
    elif action == 'star':
        new_state = not activity.get('starred', False)
        updates['starred'] = new_state
        user_activity_col.update_one({'_id': activity['_id']}, {'$set': updates})
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)

    return JsonResponse({'status': 'ok', **updates})


@staff_member_required
def user_activity_admin(request):
    """Display basic listing of user activity records for admins."""
    records = [SimpleNamespace(**doc) for doc in user_activity_col.find()]
    return render(request, 'user_activity_admin.html', {'records': records})

