"""
Django Admin configuration for Student Reward System
Provides interface for managing users, students, transactions, etc.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, StudentProfile, Transaction,
    Attendance, Product, Order
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin interface for CustomUser"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('User Information'), {
            'fields': ('role', 'is_teacher', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin interface for StudentProfile"""
    list_display = ('get_student_name', 'total_coins', 'attendance_count', 'rank', 'updated_at')
    list_filter = ('rank', 'total_coins', 'attendance_count', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('-total_coins', '-attendance_count')
    readonly_fields = ('rank', 'created_at', 'updated_at', 'total_coins', 'attendance_count')
    
    fieldsets = (
        (_('Student Information'), {
            'fields': ('user', 'total_coins', 'attendance_count', 'rank')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_student_name(self, obj):
        """Display student full name"""
        return obj.user.get_full_name() or obj.user.username
    get_student_name.short_description = _('Student Name')

    def has_add_permission(self, request):
        """Disable manual creation; profiles are auto-created"""
        return False


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction"""
    list_display = ('get_student_name', 'coins', 'transaction_type', 'get_reason_preview', 'created_by', 'created_at')
    list_filter = ('transaction_type', 'created_at', 'created_by')
    search_fields = ('student__user__username', 'reason', 'created_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Transaction Information'), {
            'fields': ('student', 'coins', 'transaction_type', 'reason', 'created_by', 'created_at')
        }),
    )

    def get_student_name(self, obj):
        """Display student full name"""
        return obj.student.user.get_full_name() or obj.student.user.username
    get_student_name.short_description = _('Student')

    def get_reason_preview(self, obj):
        """Display shortened reason"""
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    get_reason_preview.short_description = _('Reason')

    def save_model(self, request, obj, form, change):
        """Set created_by to current teacher"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin interface for Attendance"""
    list_display = ('get_student_name', 'date', 'status', 'marked_by', 'created_at')
    list_filter = ('status', 'date', 'marked_by', 'created_at')
    search_fields = ('student__user__username', 'student__user__first_name', 'student__user__last_name')
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('Attendance Information'), {
            'fields': ('student', 'date', 'status', 'marked_by', 'notes', 'created_at')
        }),
    )

    readonly_fields = ('created_at',)

    def get_student_name(self, obj):
        """Display student full name"""
        return obj.student.user.get_full_name() or obj.student.user.username
    get_student_name.short_description = _('Student')

    def save_model(self, request, obj, form, change):
        """Set marked_by to current teacher"""
        if not change:
            obj.marked_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product"""
    list_display = ('name', 'price', 'quantity_available', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'get_image_preview')
    
    fieldsets = (
        (_('Product Information'), {
            'fields': ('name', 'description', 'price', 'image', 'get_image_preview', 'quantity_available', 'is_active')
        }),
        (_('Management'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_image_preview(self, obj):
        """Show image preview"""
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" />'
        return '-'
    get_image_preview.short_description = _('Image Preview')
    get_image_preview.allow_tags = True

    def save_model(self, request, obj, form, change):
        """Set created_by to current teacher"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order"""
    list_display = ('get_order_number', 'get_student_name', 'product', 'quantity', 'coins_spent', 'created_at')
    list_filter = ('created_at', 'product')
    search_fields = ('student__user__username', 'product__name')
    ordering = ('-created_at',)
    readonly_fields = ('coins_spent', 'created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('student', 'product', 'quantity', 'coins_spent', 'created_at')
        }),
    )

    def get_order_number(self, obj):
        """Display order ID"""
        return f'Order #{obj.pk}'
    get_order_number.short_description = _('Order')

    def get_student_name(self, obj):
        """Display student full name"""
        return obj.student.user.get_full_name() or obj.student.user.username
    get_student_name.short_description = _('Student')

    def has_add_permission(self, request):
        """Disable manual order creation"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable order deletion"""
        return False


# Customize admin site
admin.site.site_header = _('Student Reward System Administration')
admin.site.site_title = _('Admin Panel')
admin.site.index_title = _('Welcome to Administration')
