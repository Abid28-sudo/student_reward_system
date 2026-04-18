"""
Models for Student Reward System
Defines: User, Student Profile, Transaction, Attendance, Product, and Order models
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Roles: 'teacher' or 'student'
    """
    ROLE_CHOICES = [
        ('teacher', _('Teacher')),
        ('student', _('Student')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name=_('Role')
    )
    is_teacher = models.BooleanField(
        default=False,
        verbose_name=_('Is Teacher')
    )
    # Teacher approval system
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Is Approved')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def is_student(self):
        return self.role == 'student'

    def is_teacher_user(self):
        return self.role == 'teacher'


class StudentProfile(models.Model):
    """
    Student Profile model to store student-specific data.
    Links to CustomUser and maintains coin balance and ranking info.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'student'},
        verbose_name=_('User')
    )
    total_coins = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Coins')
    )
    attendance_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Attendance Count')
    )
    rank = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Rank Position')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        ordering = ['-total_coins', '-attendance_count']
        verbose_name = _('Student Profile')
        verbose_name_plural = _('Student Profiles')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.total_coins} coins"

    def update_rank(self):
        """Update student's rank based on coins and attendance"""
        rank = StudentProfile.objects.filter(
            Q(total_coins__gt=self.total_coins) |
            (Q(total_coins=self.total_coins) & Q(attendance_count__gt=self.attendance_count))
        ).count() + 1
        self.rank = rank
        self.save(update_fields=['rank'])

    def add_coins(self, amount, reason=''):
        """Add coins to student's balance"""
        if amount > 0:
            self.total_coins += amount
            self.save(update_fields=['total_coins', 'updated_at'])
            return True
        return False

    def spend_coins(self, amount):
        """Deduct coins from student's balance"""
        if amount > 0 and self.total_coins >= amount:
            self.total_coins -= amount
            self.save(update_fields=['total_coins', 'updated_at'])
            return True
        return False


class TransactionType(models.TextChoices):
    """Transaction type choices"""
    REWARD = 'reward', _('Reward')
    SPEND = 'spend', _('Spend')
    ADJUSTMENT = 'adjustment', _('Adjustment')


class Transaction(models.Model):
    """
    Transaction model to track all coin movements.
    Every coin addition/deduction is logged with reason for transparency.
    """
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('Student')
    )
    coins = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Coins Amount')
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.REWARD,
        verbose_name=_('Transaction Type')
    )
    reason = models.TextField(
        blank=False,
        null=False,
        verbose_name=_('Reason'),
        help_text=_('Reason for coin transaction (mandatory)')
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions_created',
        limit_choices_to={'role': 'teacher'},
        verbose_name=_('Created By Teacher')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        indexes = [
            models.Index(fields=['student', '-created_at']),
            models.Index(fields=['created_by', '-created_at']),
        ]

    def __str__(self):
        return f"{self.student.user.username} - {self.coins} coins ({self.transaction_type})"

    def save(self, *args, **kwargs):
        """Override save to update student profile"""
        super().save(*args, **kwargs)
        # Update student's total coins
        total = Transaction.objects.filter(
            student=self.student
        ).aggregate(
            total=Sum('coins', filter=Q(transaction_type__in=['reward', 'adjustment']))
            - Sum('coins', filter=Q(transaction_type='spend'))
        )['total'] or 0
        self.student.total_coins = total
        self.student.save(update_fields=['total_coins'])


class AttendanceStatus(models.TextChoices):
    """Attendance status choices"""
    PRESENT = 'present', _('Present')
    ABSENT = 'absent', _('Absent')


class Attendance(models.Model):
    """
    Attendance model to track student presence.
    Each present mark contributes to student ranking.
    """
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('Student')
    )
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.ABSENT,
        verbose_name=_('Attendance Status')
    )
    marked_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendances',
        limit_choices_to={'role': 'teacher'},
        verbose_name=_('Marked By Teacher')
    )
    date = models.DateField(
        verbose_name=_('Date')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        ordering = ['-date']
        verbose_name = _('Attendance')
        verbose_name_plural = _('Attendances')
        unique_together = ('student', 'date')
        indexes = [
            models.Index(fields=['student', '-date']),
            models.Index(fields=['date', 'status']),
        ]

    def __str__(self):
        return f"{self.student.user.username} - {self.date} ({self.status})"

    def save(self, *args, **kwargs):
        """Override save to update attendance count"""
        super().save(*args, **kwargs)
        # Update attendance count
        attendance_count = Attendance.objects.filter(
            student=self.student,
            status=AttendanceStatus.PRESENT
        ).count()
        self.student.attendance_count = attendance_count
        self.student.save(update_fields=['attendance_count'])


class Product(models.Model):
    """
    Product model for the virtual store.
    Teachers manage products that students can purchase with coins.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Product Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    price = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Price (in coins)')
    )
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True,
        verbose_name=_('Product Image')
    )
    quantity_available = models.IntegerField(
        default=-1,  # -1 means unlimited
        validators=[MinValueValidator(-1)],
        verbose_name=_('Quantity Available (-1 for unlimited)')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products_created',
        limit_choices_to={'role': 'teacher'},
        verbose_name=_('Created By')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.price} coins"

    def is_available(self):
        """Check if product is available for purchase"""
        if not self.is_active:
            return False
        if self.quantity_available == -1:
            return True
        return self.quantity_available > 0

    def decrease_quantity(self):
        """Decrease quantity when purchased"""
        if self.quantity_available > 0:
            self.quantity_available -= 1
            self.save(update_fields=['quantity_available'])


class Order(models.Model):
    """
    Order model for student purchases from the store.
    Tracks what students bought and when.
    """
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Student')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name=_('Product')
    )
    coins_spent = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Coins Spent')
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Quantity')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Purchase Date')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        indexes = [
            models.Index(fields=['student', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Order #{self.pk} - {self.student.user.username} - {self.product.name}"

    def save(self, *args, **kwargs):
        """Override save to update student coins"""
        super().save(*args, **kwargs)
        # Deduct coins from student
        if self.student.spend_coins(self.coins_spent):
            pass  # Coins deducted successfully
        # Decrease product quantity
        if self.product:
            self.product.decrease_quantity()


# Signal handlers for automatic updates
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_student_profile(sender, instance, created, **kwargs):
    """Create StudentProfile when a new student user is created"""
    if created and instance.role == 'student':
        StudentProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=StudentProfile)
def update_all_ranks(sender, instance, **kwargs):
    """Update ranking for all students (simplified for MVP)"""
    students = StudentProfile.objects.all().order_by('-total_coins', '-attendance_count')
    for rank, student in enumerate(students, 1):
        if student.rank != rank:
            StudentProfile.objects.filter(pk=student.pk).update(rank=rank)
