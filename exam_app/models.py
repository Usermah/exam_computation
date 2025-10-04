from django.db import models
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password

CLASS_CHOICES = [
    ('SS1', 'SS1'),
    ('SS2', 'SS2'),
    ('SS3', 'SS3'),
]

TERM_CHOICES = [
    ('1', 'First Term'),
    ('2', 'Second Term'),
    ('3', 'Third Term'),
]

# ---------------------------
# Teacher Profile
# ---------------------------
class TeacherProfile(models.Model):
    name = models.CharField(max_length=150, blank=True)  # full name
    phone = models.CharField(max_length=20, blank=True)
    class_level = models.CharField(max_length=3, choices=CLASS_CHOICES, blank=True)
    is_eo = models.BooleanField(default=False, help_text="Check if this user is an Examination Officer (EO)")
    password = models.CharField(max_length=128, blank=True)  # hashed password

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name

# ---------------------------
# Student
# ---------------------------
class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    reg_no = models.CharField(max_length=30, unique=True)
    class_level = models.CharField(max_length=3, choices=CLASS_CHOICES, default='SS1')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, related_name='students')

    def __str__(self):
        return f"{self.reg_no} — {self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('view_students')

# ---------------------------
# Subject
# ---------------------------
class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# ---------------------------
# Result
# ---------------------------
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    test_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, editable=False, default=0)
    grade = models.CharField(max_length=2, editable=False, default='')
    term = models.CharField(max_length=1, choices=TERM_CHOICES)
    session = models.CharField(max_length=20, help_text="e.g. 2024/2025")
    entered_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'term', 'session')

    def save(self, *args, **kwargs):
        self.total_score = self.test_score + self.exam_score
        if self.total_score >= 70:
            self.grade = 'A'
        elif self.total_score >= 60:
            self.grade = 'B'
        elif self.total_score >= 50:
            self.grade = 'C'
        elif self.total_score >= 45:
            self.grade = 'D'
        elif self.total_score >= 40:
            self.grade = 'E'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.total_score} ({self.grade})"
