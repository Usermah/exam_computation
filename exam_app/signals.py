from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import TeacherProfile

@receiver(post_save, sender=User)
def create_teacher_profile(sender, instance, created, **kwargs):
    if created:
        # create a TeacherProfile for every new user (admin-created teachers will get a profile)
        TeacherProfile.objects.create(user=instance)
