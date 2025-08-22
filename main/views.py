from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

from .models import Question, User, UserActivity, get_next_user_id, get_or_create_activity
import random

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

        # Hash the password before storing
        hashed_password = make_password(password)

        # Create the user in PostgreSQL
        User.objects.create(
            user_id=get_next_user_id(),
            name=name,
            email=email,
            password=hashed_password,
            confirmation_password=hashed_password,
            role=role,
            school=school,
        )
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
    """Render the home page with the question count from PostgreSQL."""
    total_questions = Question.objects.count()
    return render(request, 'home.html', {'total_questions': total_questions})

def login_view(request):
    """Handle login using the users collection."""
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.filter(email=email).first()
        if user and check_password(password, user.password):
            request.session['user_name'] = user.name
            messages.success(request, f"Welcome back, {user.name}!")
            return redirect('home')
        messages.error(request, "Invalid email or password.")
        return redirect('login')

    return render(request, 'login.html')
def question_bank(request):
    """Render the initial page with session codes."""
    session_codes = list(Question.objects.values_list('session_code', flat=True).distinct())
    return render(request, 'question_bank.html', {'session_codes': session_codes})

def get_subtopics(request):
    """Return subtopics for a given session code."""
    session_code = request.GET.get('session_code')
    if not session_code:
        return JsonResponse({'error': 'Session code is required'}, status=400)

    subtopics = list(
        Question.objects.filter(session_code=session_code)
        .values_list('subtopic', flat=True)
        .distinct()
    )
    if not subtopics:
        return JsonResponse({'error': 'No subtopics found for this session code'}, status=404)

    return JsonResponse({'subtopics': subtopics})

def practice_questions(request):
    """Render the practice questions page with questions in random order."""
    session_code = request.GET.get('session_code')
    subtopic = request.GET.get('subtopic')

    if not session_code or not subtopic:
        return render(request, 'error.html', {'message': 'Session code and subtopic are required'})

    # Fetch questions matching the filters
    questions = list(Question.objects.filter(session_code=session_code, subtopic=subtopic))
    random.shuffle(questions)
    return render(request, 'practice_questions.html', {'questions': questions})

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

@csrf_exempt
def check_answer(request):
    question_id = request.POST.get('question_id')
    selected_answer = request.POST.get('selected_answer')
    doc = Question.objects.filter(question_id=question_id).first()
    is_correct = doc and doc.answer == selected_answer
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

    user = User.objects.filter(name=request.session['user_name']).first()
    if not user:
        return JsonResponse({'error': 'User not found'}, status=404)

    question = Question.objects.filter(question_id=question_id).first()
    if not question:
        return JsonResponse({'error': 'Question not found'}, status=404)

    activity = get_or_create_activity(user, question)
    updates = {}

    if action == 'start':
        activity.time_started = timezone.now()
        activity.times_viewed += 1
        activity.save()
        updates['time_started'] = activity.time_started
    elif action == 'answer':
        correct = request.POST.get('correct') == 'true'
        if activity.time_started:
            activity.time_took = timezone.now() - activity.time_started
        activity.solved = True
        activity.correct = correct
        activity.save()
        updates = {
            'solved': activity.solved,
            'correct': activity.correct,
            'time_took': activity.time_took,
        }
    elif action == 'bookmark':
        activity.bookmarked = not activity.bookmarked
        activity.save()
        updates['bookmarked'] = activity.bookmarked
    elif action == 'star':
        activity.starred = not activity.starred
        activity.save()
        updates['starred'] = activity.starred
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)

    return JsonResponse({'status': 'ok', **updates})


@staff_member_required
def user_activity_admin(request):
    """Display user activity records with summary statistics for admins."""
    records = list(UserActivity.objects.all())

    summary = {
        "total_users": User.objects.count(),
        "total_questions": Question.objects.count(),
        "total_records": UserActivity.objects.count(),
        "solved": UserActivity.objects.filter(solved=True).count(),
        "correct": UserActivity.objects.filter(correct=True).count(),
        "starred": UserActivity.objects.filter(starred=True).count(),
        "bookmarked": UserActivity.objects.filter(bookmarked=True).count(),
    }

    context = {
        "records": records,
        "summary": summary,
    }
    return render(request, "user_activity_admin.html", context)

