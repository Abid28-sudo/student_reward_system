"""
Custom Django management command to create demo data
Usage: python manage.py create_demo_data
"""

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from rewards_app.models import CustomUser, StudentProfile, Product, Transaction, Attendance, AttendanceStatus, TransactionType
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = _('Creates demo data for testing the Student Reward System')

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating demo data...'))
        
        # Create demo teacher
        teacher, created = CustomUser.objects.get_or_create(
            username='teacher123',
            defaults={
                'email': 'teacher@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'teacher',
                'is_teacher': True,
            }
        )
        if created:
            teacher.set_password('password123')
            teacher.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created teacher: {teacher.username}'))
        
        # Create demo students
        student_names = [
            ('Ahmed', 'Ali'),
            ('Fatima', 'Hassan'),
            ('Mohammed', 'Ibrahim'),
            ('Layla', 'Ahmed'),
            ('Omar', 'Hassan'),
        ]
        
        students = []
        for first_name, last_name in student_names:
            username = f'student_{first_name.lower()}'
            student, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'student',
                }
            )
            if created:
                student.set_password('password123')
                student.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created student: {student.username}'))
            students.append(student)
        
        # Create demo products
        products_data = [
            ('Notebook', 'Premium notebook for notes', 10),
            ('Pen Set', 'Set of 5 colored pens', 8),
            ('T-Shirt', 'School T-Shirt with logo', 50),
            ('Water Bottle', 'Reusable water bottle', 15),
            ('Backpack', 'School backpack', 100),
            ('Sticker Pack', 'Motivational sticker pack', 5),
            ('Headphones', 'Basic earphones', 30),
            ('Book', 'Educational book', 25),
        ]
        
        for name, description, price in products_data:
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'price': price,
                    'quantity_available': -1,  # Unlimited
                    'is_active': True,
                    'created_by': teacher,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created product: {product.name}'))
        
        # Add demo coins and attendance
        for idx, student in enumerate(students, 1):
            # Add coins
            coins = (idx * 20) + 10
            Transaction.objects.create(
                student=student.student_profile,
                coins=coins,
                transaction_type=TransactionType.REWARD,
                reason=f'Demo coins for {student.get_full_name()}',
                created_by=teacher
            )
            
            # Add attendance records
            for day in range(1, 11):
                Attendance.objects.create(
                    student=student.student_profile,
                    status=AttendanceStatus.PRESENT if day % 2 == 0 else AttendanceStatus.PRESENT,
                    date=timezone.now().date() - timedelta(days=day),
                    marked_by=teacher,
                    notes=f'Attendance for day {day}'
                )
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Added coins and attendance for: {student.get_full_name()}'
            ))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Demo data created successfully!'))
        self.stdout.write(self.style.WARNING('\nDemo Credentials:'))
        self.stdout.write('Teacher: teacher123 / password123')
        self.stdout.write('Students: student_ahmed, student_fatima, etc. / password123')
