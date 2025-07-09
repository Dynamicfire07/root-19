from django.contrib import admin
from .models import Question, User, UserActivity

# Register Question
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'session_code', 'subtopic', 'answer')  # Customize fields displayed

# Register User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'email', 'role', 'school')  # Include user_id in admin display
    search_fields = ('name', 'email', 'user_id')  # Add search functionality
    list_filter = ('role', 'school')  # Filter options in admin panel

# Register UserActivity
from django.contrib import admin
from .models import UserActivity

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'solved', 'correct', 'bookmarked', 'starred', 'times_viewed', 'time_took')
    search_fields = ('user__user_id', 'question__question_id')  # Allow search by user_id and question_id
    list_filter = ('solved', 'correct', 'bookmarked', 'starred')  # Add filters for boolean fields