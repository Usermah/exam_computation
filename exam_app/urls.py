from django.urls import path
from . import views

urlpatterns = [
    # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/add-student/', views.add_student, name='add_student'),
    path('teacher/view-students/', views.view_students, name='view_students'),
    path('teacher/input-results/', views.input_results, name='input_results'),

    # EO URLs
    path('eo/dashboard/', views.eo_dashboard, name='eo_dashboard'),
    path('eo/view-results/', views.view_all_results, name='view_all_results'),
    # path('eo/compile-results/', views.compile_results, name='compile_results'),

    # Login / logout
    path('login/', views.teacher_login_view, name='teacher_login'),
    path('logout/', views.teacher_logout, name='teacher_logout'),
    path('graded-students/', views.graded_students, name='graded_students'),

]
