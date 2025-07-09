from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt

from .models import Question, User

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

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Save the user to the database
        user = User(
            name=name,
            email=email,
            password=password,  # Store raw password (not secure for production)
            role=role,
            school=school
        )
        user.save()
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
    """Render the home page."""
    total_questions = Question.objects.count()  # Get total number of questions
    return render(request, 'home.html', {'total_questions': total_questions})

def login_view(request):
    """Handle login."""
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email, password=password)
            request.session['user_name'] = user.name  # Store user name in session
            messages.success(request, f"Welcome back, {user.name}!")
            return redirect('home')  # Redirect to home page on success
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'login.html')
def question_bank(request):
    """Render the initial page with session codes."""
    session_codes = Question.objects.values_list('session_code', flat=True).distinct()
    return render(request, 'question_bank.html', {'session_codes': session_codes})
    print(session_codes)

def get_subtopics(request):
    """Return subtopics for a given session code."""
    session_code = request.GET.get('session_code')
    if not session_code:
        return JsonResponse({'error': 'Session code is required'}, status=400)
    
    subtopics = Question.objects.filter(session_code=session_code).values_list('subtopic', flat=True).distinct()
    if not subtopics:
        return JsonResponse({'error': 'No subtopics found for this session code'}, status=404)

    return JsonResponse({'subtopics': list(subtopics)})

import random
from django.shortcuts import render
from .models import Question

def practice_questions(request):
    """Render the practice questions page with questions in random order."""
    session_code = request.GET.get('session_code')
    subtopic = request.GET.get('subtopic')

    if not session_code or not subtopic:
        return render(request, 'error.html', {'message': 'Session code and subtopic are required'})

    # Fetch the questions based on session code and subtopic
    questions = list(Question.objects.filter(session_code=session_code, subtopic=subtopic))

    # Shuffle the questions to randomize the order
    random.shuffle(questions)

    # Return the randomized questions to the template
    return render(request, 'practice_questions.html', {'questions': questions})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def check_answer(request):
    question_id = request.POST.get('question_id')
    selected_answer = request.POST.get('selected_answer')
    question = Question.objects.get(question_id=question_id)
    is_correct = question.answer == selected_answer
    return JsonResponse({'is_correct': is_correct})

