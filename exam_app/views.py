from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TeacherLoginForm, StudentForm, ResultForm
from .models import TeacherProfile, Student, Result, Subject
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

# Helper: get logged-in teacher
def get_logged_in_teacher(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        return None
    try:
        return TeacherProfile.objects.get(id=teacher_id)
    except TeacherProfile.DoesNotExist:
        request.session.flush()
        return None

# Teacher / EO Login
def teacher_login_view(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['teacher']
            request.session['teacher_id'] = teacher.id
            messages.success(request, f"Welcome, {teacher.name}!")
            return redirect('eo_dashboard' if teacher.is_eo else 'teacher_dashboard')
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = TeacherLoginForm()
    return render(request, 'login.html', {'form': form})

# Logout
def teacher_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('teacher_login')

# Teacher Dashboard
def teacher_dashboard(request):
    teacher = get_logged_in_teacher(request)
    if not teacher:
        return redirect('teacher_login')
    students = Student.objects.filter(class_level=teacher.class_level)
    recent_results = Result.objects.filter(entered_by=teacher).order_by('-created_at')[:8]
    return render(request, 'teacher_dashboard.html', {
        'teacher': teacher,
        'students': students,
        'recent_results': recent_results
    })

# EO Dashboard
def eo_dashboard(request):
    teacher = get_logged_in_teacher(request)
    if not teacher:
        messages.error(request, "You must log in first.")
        return redirect('teacher_login')
    if not teacher.is_eo:
        messages.error(request, "Access denied. EO only.")
        return redirect('teacher_dashboard')
    return render(request, 'eo_dashboard.html', {'teacher': teacher})

# Add Student
def add_student(request):
    teacher = get_logged_in_teacher(request)
    if not teacher:
        return redirect('teacher_login')
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.teacher = teacher
            student.class_level = teacher.class_level
            student.save()
            messages.success(request, f"Student {student} added successfully.")
            return redirect('view_students')
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {
        'form': form,
        'teacher': teacher
    })

# View Students
def view_students(request):
    teacher = get_logged_in_teacher(request)
    if not teacher:
        return redirect('teacher_login')
    students = Student.objects.filter(class_level=teacher.class_level)
    return render(request, 'view_students.html', {
        'students': students,
        'teacher': teacher  # ✅ added so navbar shows Logout & name
    })

# Input Results
def input_results(request):
    teacher = get_logged_in_teacher(request)
    if not teacher:
        return redirect('teacher_login')
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            if result.student.class_level != teacher.class_level:
                messages.error(request, "You can only enter results for your class.")
            else:
                result.entered_by = teacher
                result.save()
                messages.success(request, "Result saved successfully.")
                return redirect('teacher_dashboard')
    else:
        form = ResultForm()
        form.fields['student'].queryset = Student.objects.filter(class_level=teacher.class_level)
        form.fields['subject'].queryset = Subject.objects.all()
    return render(request, 'input_results.html', {
        'form': form,
        'teacher': teacher  # ✅ added
    })

# EO: View All Resultsfrom django.db.models import Sum, Avg
# from django.shortcuts import render, redirect
from django.http import HttpResponse
# from django.db.models import Avg
import csv

def view_all_results(request):
    teacher = get_logged_in_teacher(request)
    if not teacher:
        return redirect('teacher_login')
    if not teacher.is_eo:
        messages.error(request, "Access denied. EO only.")
        return redirect('teacher_dashboard')

    # CSV download (flat list)
    if request.GET.get("download") == "csv":
        results_qs = Result.objects.select_related('student', 'subject').order_by(
            'student__class_level', 'subject__name', 'student__last_name', 'student__first_name'
        )

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="all_results.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student', 'Class', 'Subject', 'Total Score', 'Grade', 'Term', 'Session'])

        for r in results_qs:
            writer.writerow([
                f"{r.student.first_name} {r.student.last_name}",
                r.student.class_level,
                r.subject.name if r.subject else '',
                r.total_score,
                r.grade,
                r.term,
                r.session
            ])
        return response

    # Normal page render: group by class -> subject -> [results]
    results_qs = Result.objects.select_related('student', 'subject').order_by(
        'student__class_level', 'subject__name', 'student__last_name', 'student__first_name'
    )

    grouped_temp = {}  # temporary structure: { class_name: { subject_name: [result, ...] } }
    for r in results_qs:
        class_name = r.student.class_level or "Unknown"
        subject_name = r.subject.name if r.subject else "Unknown"
        grouped_temp.setdefault(class_name, {}).setdefault(subject_name, []).append(r)

    # Convert grouped_temp to a list of class dicts with averages to make template access easy
    classes = []
    for class_name, subjects in grouped_temp.items():
        # collect all total_score values for this class to compute average
        scores = []
        for subject_results in subjects.values():
            for rr in subject_results:
                try:
                    scores.append(float(rr.total_score))
                except Exception:
                    # fallback if Decimal or None etc.
                    try:
                        scores.append(float(str(rr.total_score)))
                    except Exception:
                        pass
        average = (sum(scores) / len(scores)) if scores else 0
        classes.append({
            'class_name': class_name,
            'average': average,
            'subjects': subjects  # dict: subject_name -> [Result,...]
        })

    # optional: sort classes by name
    classes.sort(key=lambda c: c['class_name'])

    return render(request, 'eo_view_results.html', {
        'classes': classes,
        'teacher': teacher,
    })

# EO: Compile Results
# def compile_results(request):
#     teacher = get_logged_in_teacher(request)
#     if not teacher:
#         return redirect('teacher_login')
#     if not teacher.is_eo:
#         messages.error(request, "Access denied. EO only.")
#         return redirect('teacher_dashboard')
#     return render(request, 'eo_compile_results.html', {
#         'teacher': teacher
#     })

def graded_students(request):
    teacher = get_logged_in_teacher(request)
    if not teacher:
        return redirect('teacher_login')

    graded = (
        Result.objects
        .filter(entered_by=teacher)
        .values(
            'subject__name',
            'student__id',
            'student__reg_no',
            'student__first_name',
            'student__last_name',
            'student__class_level'
        )
        .annotate(total_marks=Sum('total_score'))
        .order_by('subject__name')
    )

    grouped_by_subject = {}
    for item in graded:
        subject = item['subject__name']
        if subject not in grouped_by_subject:
            grouped_by_subject[subject] = []
        grouped_by_subject[subject].append(item)

    return render(request, 'graded_students.html', {
        'grouped_by_subject': grouped_by_subject,
        'teacher': teacher  # ✅ added
    })
