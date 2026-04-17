"""
Unit tests for Student Reward System models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rewards_app.models import (
    CustomUser, StudentProfile, Transaction, Attendance,
    Product, Order, AttendanceStatus, TransactionType
)

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test CustomUser model"""
    
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username='teacher1',
            email='teacher@test.com',
            password='testpass123',
            role='teacher'
        )
        self.student = CustomUser.objects.create_user(
            username='student1',
            email='student@test.com',
            password='testpass123',
            role='student'
        )
    
    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(self.teacher.role, 'teacher')
        self.assertEqual(self.student.role, 'student')
        self.assertTrue(self.teacher.is_teacher_user())
        self.assertTrue(self.student.is_student())
    
    def test_student_profile_auto_creation(self):
        """Test that StudentProfile is auto-created for students"""
        self.assertTrue(hasattr(self.student, 'student_profile'))
        self.assertIsInstance(self.student.student_profile, StudentProfile)


class StudentProfileModelTest(TestCase):
    """Test StudentProfile model"""
    
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            username='student1',
            email='student@test.com',
            password='testpass123',
            role='student'
        )
        self.profile = self.student.student_profile
    
    def test_profile_initial_values(self):
        """Test initial profile values"""
        self.assertEqual(self.profile.total_coins, 0)
        self.assertEqual(self.profile.attendance_count, 0)
    
    def test_add_coins(self):
        """Test adding coins"""
        result = self.profile.add_coins(50)
        self.assertTrue(result)
        self.assertEqual(self.profile.total_coins, 50)
    
    def test_spend_coins(self):
        """Test spending coins"""
        self.profile.total_coins = 100
        self.profile.save()
        
        result = self.profile.spend_coins(30)
        self.assertTrue(result)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_coins, 70)
    
    def test_spend_coins_insufficient(self):
        """Test spending with insufficient coins"""
        self.profile.total_coins = 10
        self.profile.save()
        
        result = self.profile.spend_coins(50)
        self.assertFalse(result)


class TransactionModelTest(TestCase):
    """Test Transaction model"""
    
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username='teacher1',
            password='testpass123',
            role='teacher'
        )
        self.student = CustomUser.objects.create_user(
            username='student1',
            password='testpass123',
            role='student'
        )
    
    def test_reward_transaction(self):
        """Test creating reward transaction"""
        transaction = Transaction.objects.create(
            student=self.student.student_profile,
            coins=50,
            transaction_type=TransactionType.REWARD,
            reason='Good performance',
            created_by=self.teacher
        )
        self.assertEqual(transaction.coins, 50)
        self.assertEqual(transaction.transaction_type, TransactionType.REWARD)


class AttendanceModelTest(TestCase):
    """Test Attendance model"""
    
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username='teacher1',
            password='testpass123',
            role='teacher'
        )
        self.student = CustomUser.objects.create_user(
            username='student1',
            password='testpass123',
            role='student'
        )
    
    def test_mark_present(self):
        """Test marking student present"""
        from django.utils import timezone
        
        attendance = Attendance.objects.create(
            student=self.student.student_profile,
            status=AttendanceStatus.PRESENT,
            date=timezone.now().date(),
            marked_by=self.teacher
        )
        self.assertEqual(attendance.status, AttendanceStatus.PRESENT)


class ProductModelTest(TestCase):
    """Test Product model"""
    
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username='teacher1',
            password='testpass123',
            role='teacher'
        )
    
    def test_product_creation(self):
        """Test product creation"""
        product = Product.objects.create(
            name='Notebook',
            description='A notebook',
            price=10,
            created_by=self.teacher
        )
        self.assertEqual(product.name, 'Notebook')
        self.assertEqual(product.price, 10)
    
    def test_product_availability(self):
        """Test product availability check"""
        product = Product.objects.create(
            name='Limited Item',
            price=20,
            quantity_available=5,
            is_active=True,
            created_by=self.teacher
        )
        self.assertTrue(product.is_available())
        
        # Make unavailable
        product.is_active = False
        product.save()
        self.assertFalse(product.is_available())
