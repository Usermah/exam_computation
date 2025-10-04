from django import forms
from .models import Student, Result, Subject
from django.contrib.auth.hashers import check_password
from .models import TeacherProfile

# ---------------------------
# Teacher Login Form
# ---------------------------
from django import forms
from django.contrib.auth.hashers import check_password
from .models import TeacherProfile

class TeacherLoginForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        password = cleaned_data.get("password")
        if name and password:
            try:
                teacher = TeacherProfile.objects.get(name__iexact=name)
                if not teacher.check_password(password):
                    raise forms.ValidationError("Incorrect password.")
                cleaned_data['teacher'] = teacher
            except TeacherProfile.DoesNotExist:
                raise forms.ValidationError("Teacher not found.")
        return cleaned_data


# ---------------------------
# Add Student Form
# ---------------------------
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'reg_no']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'reg_no': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ---------------------------
# Result Form
# ---------------------------
# ---------------------------
# Result Form (Fixed)
# ---------------------------
class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'subject', 'test_score', 'exam_score', 'term', 'session']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'test_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'exam_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2024/2025'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        subject = cleaned_data.get('subject')
        term = cleaned_data.get('term')
        session = cleaned_data.get('session')

        # Only validate if all fields are present
        if student and subject and term and session:
            exists = Result.objects.filter(
                student=student,
                subject=subject,
                term=term,
                session=session
            ).exists()

            if exists:
                raise forms.ValidationError(
                    f"Result for {student} in {subject} for Term {term} ({session}) already exists."
                )

        return cleaned_data

# ---------------------------
# Subject Form
# ---------------------------
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}
