from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt

from .db import questions_col, users_col, user_activity_col, get_next_user_id
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

        # Insert the user document into MongoDB
        users_col.insert_one({
            'user_id': get_next_user_id(),
            'name': name,
            'email': email,
            'password': password,  # Store raw password (not secure for production)
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
        user = users_col.find_one({'email': email, 'password': password})
        if user:
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

def get_random_questions(session_code, subtopic, exclude=None, limit=10):
    """Fetch a random subset of questions using MongoDB's $sample stage."""
    match_stage = {'session_code': session_code, 'subtopic': subtopic}
    if exclude:
        match_stage['question_id'] = {'$nin': exclude}
    pipeline = [
        {'$match': match_stage},
        {'$sample': {'size': limit}},
    ]
    return list(questions_col.aggregate(pipeline))


def practice_questions(request):
    """Render the practice questions page with an initial batch of questions."""
    session_code = request.GET.get('session_code')
    subtopic = request.GET.get('subtopic')

    if not session_code or not subtopic:
        return render(request, 'error.html', {'message': 'Session code and subtopic are required'})

    docs = get_random_questions(session_code, subtopic, limit=10)
    questions = [SimpleNamespace(**doc) for doc in docs]
    context = {
        'questions': questions,
        'session_code': session_code,
        'subtopic': subtopic,
    }
    return render(request, 'practice_questions.html', context)


def fetch_questions(request):
    """Return additional questions for asynchronous loading."""
    session_code = request.GET.get('session_code')
    subtopic = request.GET.get('subtopic')
    exclude = request.GET.getlist('exclude[]') or request.GET.get('exclude', '')
    if isinstance(exclude, str):
        exclude = [e for e in exclude.split(',') if e]
    limit = int(request.GET.get('limit', 10))

    docs = get_random_questions(session_code, subtopic, exclude, limit)
    questions = []
    for doc in docs:
        questions.append({
            'question_id': doc.get('question_id'),
            'image_base64': doc.get('image_base64'),
            'answer': doc.get('answer'),
        })
    return JsonResponse({'questions': questions})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def check_answer(request):
    question_id = request.POST.get('question_id')
    selected_answer = request.POST.get('selected_answer')
    doc = questions_col.find_one({'question_id': question_id})
    is_correct = doc and doc.get('answer') == selected_answer
    return JsonResponse({'is_correct': is_correct})

