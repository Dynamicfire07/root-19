"""Django ORM models for the application using PostgreSQL."""

from django.db import models


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

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.question_id


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    confirmation_password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=[("Student", "Student"), ("Teacher", "Teacher")])
    school = models.CharField(max_length=150)
    user_id = models.CharField(max_length=10, unique=True, editable=False)

    def __str__(self) -> str:  # pragma: no cover
        return self.user_id


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    solved = models.BooleanField(default=False)
    correct = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    starred = models.BooleanField(default=False)
    times_viewed = models.IntegerField(default=0)
    time_started = models.DateTimeField(null=True, blank=True)
    time_took = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "question")


def get_next_user_id() -> str:
    """Generate a simple incremental user_id like U1, U2, ..."""
    last = User.objects.order_by("-user_id").first()
    if last and last.user_id.startswith("U"):
        try:
            num = int(last.user_id[1:])
            return f"U{num + 1}"
        except ValueError:
            pass
    return "U1"


def get_or_create_activity(user: User, question: Question) -> "UserActivity":
    """Fetch a user/question activity record or create a default one."""
    activity, _ = UserActivity.objects.get_or_create(user=user, question=question)
    return activity

