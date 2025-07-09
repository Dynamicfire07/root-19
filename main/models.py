from django.db import models


db = "mongodb+srv://shauryajain377:root19@root19.4ofompm.mongodb.net/?retryWrites=true&w=majority&appName=root19"
class Question(models.Model):
    question_id = models.CharField(max_length=100, unique=True)
    session_code = models.CharField(max_length=50)
    session = models.CharField(max_length=50)
    year = models.IntegerField()
    paper_code = models.CharField(max_length=50)
    variant = models.CharField(max_length=50)
    file_question = models.CharField(max_length=255)
    subtopic = models.CharField(max_length=255)
    extracted_text = models.TextField()
    image_base64 = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return f"Question {self.question_id}"
    

from django.db import models

class User(models.Model):
    user_id = models.CharField(max_length=10, unique=True, editable=False)  # Unique ID like U1, U2
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    confirmation_password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=[('Student', 'Student'), ('Teacher', 'Teacher')])
    school = models.CharField(max_length=150)

    def save(self, *args, **kwargs):
        # Automatically generate a unique user_id
        if not self.user_id:
            last_user = User.objects.order_by('-id').first()  # Get the last user
            if last_user:
                last_id = int(last_user.user_id[1:])  # Extract the numeric part of the user_id
                self.user_id = f'U{last_id + 1}'  # Increment by 1
            else:
                self.user_id = 'U1'  # First user starts with U1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id} - {self.name} ({self.role})"

    def __str__(self):
        return f"{self.name} ({self.role})"
    
from django.db import models
from django.utils.timezone import now

class UserActivity(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)  # Link to User
    question = models.ForeignKey('Question', on_delete=models.CASCADE)  # Link to Question
    solved = models.BooleanField(default=False)  # Whether the question was solved
    correct = models.BooleanField(default=False)  # Whether the answer was correct
    bookmarked = models.BooleanField(default=False)  # Whether the question was bookmarked
    starred = models.BooleanField(default=False)  # Whether the question was starred
    times_viewed = models.IntegerField(default=0)  # How many times the question was viewed
    time_started = models.DateTimeField(null=True, blank=True)  # Start time
    time_took = models.DurationField(null=True, blank=True)  # Time taken to solve

    def __str__(self):
        return f"{self.user.user_id} - {self.question.question_id}"