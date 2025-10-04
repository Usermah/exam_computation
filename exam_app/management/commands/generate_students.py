import random
from django.core.management.base import BaseCommand
from exam_app.models import Student, TeacherProfile

FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Daniel", "Laura", "James", "Olivia"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
CLASS_CHOICES = ['SS1', 'SS2', 'SS3']

class Command(BaseCommand):
    help = "Generate random students"

    def add_arguments(self, parser):
        parser.add_argument(
            '--total',
            type=int,
            default=1000,  # safe default
            help='Total number of students to generate'
        )

    def handle(self, *args, **options):
        total = options['total']
        students = []

        for i in range(total):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            reg_no = f"STU{str(i+1).zfill(7)}"
            class_level = random.choice(CLASS_CHOICES)

            # Optional: assign a random teacher of that class
            teacher_qs = TeacherProfile.objects.filter(class_level=class_level)
            teacher = random.choice(teacher_qs) if teacher_qs.exists() else None

            students.append(Student(
                first_name=first_name,
                last_name=last_name,
                reg_no=reg_no,
                class_level=class_level,
                teacher=teacher
            ))

            # Bulk insert in chunks of 10k to avoid memory issues
            if len(students) >= 10000:
                Student.objects.bulk_create(students)
                students = []
                self.stdout.write(self.style.SUCCESS(f'{i+1} students added...'))

        # Insert remaining students
        if students:
            Student.objects.bulk_create(students)

        self.stdout.write(self.style.SUCCESS(f'Total {total} students generated successfully!'))
