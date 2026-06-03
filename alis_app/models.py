from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('owner', 'Owner (Super Admin)'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # Intelligence specific fields
    level = models.CharField(max_length=20, default='Weak', null=True, blank=True)
    last_quiz_score = models.IntegerField(null=True, blank=True)
    last_subject = models.CharField(max_length=50, null=True, blank=True)
    easy_accuracy = models.IntegerField(null=True, blank=True)
    medium_accuracy = models.IntegerField(null=True, blank=True)
    hard_accuracy = models.IntegerField(null=True, blank=True)
    weak_areas = models.JSONField(default=list, null=True, blank=True)
    
    # Extended Intelligence DNA
    risk_score = models.FloatField(default=0.0) # 0 to 100
    learning_speed = models.FloatField(default=0.0) # percentage or rate
    retention_score = models.FloatField(default=0.0) # 0 to 100
    learning_trend = models.JSONField(default=list) # [{date, score}]
    learning_dna = models.CharField(max_length=100, default="Analytical")
    
    # XP & Achievement System
    xp = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0)
    user_level = models.IntegerField(default=1) 
    badges = models.JSONField(default=list, null=True, blank=True)
    streak_days = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    # Career Readiness Index (0 to 100)
    technical_readiness = models.FloatField(default=0.0)
    aptitude_readiness = models.FloatField(default=0.0)
    communication_readiness = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.first_name or self.username} ({self.role})"

class TutorMessage(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutor_messages')
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('ai', 'AI')])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.student.username} - {self.role}: {self.content[:30]}..."

class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Concept(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='concepts')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.subject.name} - {self.name}"

class Assessment(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assessments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=20, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')])
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    concept = models.ForeignKey(Concept, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    difficulty = models.CharField(max_length=20, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')])

    def __str__(self):
        return f"{self.assessment.title} - {self.text[:50]}"

class AssessmentResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_results')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.IntegerField()
    strong_concepts = models.JSONField(default=list)
    weak_concepts = models.JSONField(default=list)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.assessment.title} - {self.score}%"

class RecommendationItem(models.Model):
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='recommendations')
    TYPE_CHOICES = [
        ('Video', 'Video'),
        ('Article', 'Article'),
        ('Practice', 'Practice'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.concept.name} - {self.type} - {self.title}"

class ClassGroup(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_classes')
    name = models.CharField(max_length=100)
    students = models.ManyToManyField(User, related_name='enrolled_classes', limit_choices_to={'role': 'student'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.teacher.username})"

class Assignment(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Resource(models.Model):
    TYPE_CHOICES = [
        ('PDF', 'PDF Document'),
        ('Video', 'Video Lecture'),
        ('Note', 'Study Note'),
        ('Link', 'External Link'),
    ]
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('owner', 'Owner'),
        ('all', 'All Roles'),
    ]
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    target_role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='all')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AIUsageLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage_logs')
    prompt = models.TextField()
    response_summary = models.TextField()
    role_context = models.CharField(max_length=20) # student, teacher, etc.
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"

class PlatformMetric(models.Model):
    date = models.DateField(default=timezone.now)
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ai_requests_count = models.IntegerField(default=0)
    system_health_score = models.IntegerField(default=100) # 0 to 100

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Metrics for {self.date}"
