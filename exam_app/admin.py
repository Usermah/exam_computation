from django.contrib import admin
from .models import TeacherProfile, Student, Subject, Result

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'class_level', 'is_eo')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('reg_no', 'first_name', 'last_name', 'class_level', 'teacher')
    search_fields = ('reg_no', 'first_name', 'last_name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'test_score', 'exam_score', 'total_score',
                    'grade', 'term', 'session', 'entered_by', 'created_at')
    list_filter = ('term', 'session', 'subject')
    search_fields = ('student__reg_no', 'student__first_name')
