from django.apps import AppConfig

class ExamAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exam_app'

    def ready(self):
        # import signals to auto-create TeacherProfile when a new User is created
        import exam_app.signals
