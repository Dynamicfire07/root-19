from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('get-subtopics/', views.get_subtopics, name='get_subtopics'),
    path('practice-questions/', views.practice_questions, name='practice_questions'),
    path('fetch-questions/', views.fetch_questions, name='fetch_questions'),
    path('check-answer/', views.check_answer, name='check_answer'),
    path('question-bank/', views.question_bank, name='question_bank'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]

