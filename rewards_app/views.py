"""
Views for Student Reward System
Handles all HTTP requests for login, dashboards, CRUD operations, etc.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_GET
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from functools import wraps
from datetime import timedelta
from django.utils import timezone

from .models import (
    CustomUser, StudentProfile, Transaction, Attendance,
    Product, Order, AttendanceStatus, TransactionType
)
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, RewardStudentForm,
    MarkAttendanceForm, AddProductForm, PurchaseProductForm
)


# ============================================================================
# DECORATORS FOR ROLE-BASED ACCESS CONTROL
# ============================================================================

def teacher_required(view_func):
    """Decorator to restrict access to teachers only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('rewards_app:login')
        if request.user.role != 'teacher':
            messages.error(request, _('You do not have permission to access this page.'))
            if request.user.role == 'student':
                return redirect('rewards_app:student_dashboard')
            return redirect('rewards_app:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """Decorator to restrict access to students only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('rewards_app:login')
        if request.user.role != 'student':
            messages.error(request, _('You do not have permission to access this page.'))
            if request.user.role == 'teacher':
                return redirect('rewards_app:teacher_dashboard')
            return redirect('rewards_app:home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def home(request):
    """Home page - redirects based on user role"""
    if request.user.is_authenticated:
        if request.user.role == 'teacher':
            return redirect('rewards_app:teacher_dashboard')
        elif request.user.role == 'student':
            return redirect('rewards_app:student_dashboard')
    return render(request, 'rewards_app/home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, _('Registration successful! Please log in.'))
            return redirect('rewards_app:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'rewards_app/register.html', {'form': form})


def login_view(request):
    """Custom login view with role-based redirection"""
    if request.user.is_authenticated:
        if request.user.role == 'teacher':
            return redirect('rewards_app:teacher_dashboard')
        return redirect('rewards_app:student_dashboard')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Role-based redirection
            if user.role == 'teacher':
                messages.success(request, _('Welcome back, Teacher!'))
                return redirect('rewards_app:teacher_dashboard')
            else:
                messages.success(request, _('Welcome back, Student!'))
                return redirect('rewards_app:student_dashboard')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'rewards_app/login.html', {'form': form})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, _('You have been logged out successfully.'))
    return redirect('rewards_app:home')


# ============================================================================
# TEACHER VIEWS
# ============================================================================

@teacher_required
def teacher_dashboard(request):
    """Teacher main dashboard"""
    context = {
        'total_students': StudentProfile.objects.count(),
        'top_coins_students': StudentProfile.objects.all()[:5],
        'top_attendance_students': StudentProfile.objects.order_by('-attendance_count')[:5],
        'recent_transactions': Transaction.objects.select_related('student', 'created_by').order_by('-created_at')[:10],
        'recent_attendances': Attendance.objects.select_related('student').order_by('-date')[:10],
    }
    return render(request, 'rewards_app/teacher/dashboard.html', context)


@teacher_required
def manage_students(request):
    """List all students - CRUD interface"""
    students = StudentProfile.objects.select_related('user').order_by('-total_coins')
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'students': page_obj.object_list,
    }
    return render(request, 'rewards_app/teacher/manage_students.html', context)


@teacher_required
def student_detail(request, student_id):
    """View detailed student information and history"""
    student = get_object_or_404(StudentProfile, pk=student_id)
    transactions = student.transactions.all().order_by('-created_at')[:20]
    attendances = student.attendances.all().order_by('-date')[:20]
    orders = student.orders.select_related('product').order_by('-created_at')[:10]
    
    # Calculate statistics
    attendance_percentage = 0
    total_attendance_records = student.attendances.count()
    if total_attendance_records > 0:
        present_count = student.attendances.filter(status=AttendanceStatus.PRESENT).count()
        attendance_percentage = (present_count / total_attendance_records) * 100
    
    context = {
        'student': student,
        'transactions': transactions,
        'attendances': attendances,
        'orders': orders,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'rewards_app/teacher/student_detail.html', context)


@teacher_required
def add_student(request):
    """Add new student"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Force role to student
            user = form.save(commit=False)
            user.role = 'student'
            user.save()
            messages.success(request, _('Student added successfully!'))
            return redirect('rewards_app:manage_students')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'rewards_app/teacher/add_student.html', {'form': form})


@teacher_required
@require_POST
def delete_student(request, student_id):
    """Delete a student (soft delete - deactivate instead)"""
    student = get_object_or_404(StudentProfile, pk=student_id)
    student.user.is_active = False
    student.user.save()
    messages.success(request, _('Student deactivated successfully.'))
    return redirect('rewards_app:manage_students')


@teacher_required
def reward_student(request):
    """Reward student with coins"""
    if request.method == 'POST':
        form = RewardStudentForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            coins = form.cleaned_data['coins']
            reason = form.cleaned_data['reason']
            
            # Create transaction
            transaction = Transaction.objects.create(
                student=student,
                coins=coins,
                transaction_type=TransactionType.REWARD,
                reason=reason,
                created_by=request.user
            )
            
            # Update student coins
            student.add_coins(coins)
            student.update_rank()
            
            messages.success(
                request,
                _('Rewarded %(student)s with %(coins)d coins!') % {
                    'student': student.user.get_full_name(),
                    'coins': coins
                }
            )
            return redirect('rewards_app:teacher_dashboard')
    else:
        form = RewardStudentForm()
    
    return render(request, 'rewards_app/teacher/reward_student.html', {'form': form})


@teacher_required
def mark_attendance(request):
    """Mark student attendance"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        status = request.POST.get('status')
        date_str = request.POST.get('date')
        notes = request.POST.get('notes', '')
        
        student = get_object_or_404(StudentProfile, pk=student_id)
        
        # Create or update attendance
        attendance, created = Attendance.objects.update_or_create(
            student=student,
            date=date_str,
            defaults={
                'status': status,
                'marked_by': request.user,
                'notes': notes
            }
        )
        
        # Update student's attendance count
        student.attendance_count = student.attendances.filter(status=AttendanceStatus.PRESENT).count()
        student.save(update_fields=['attendance_count'])
        student.update_rank()
        
        messages.success(request, _('Attendance marked successfully!'))
        return redirect('rewards_app:manage_students')
    
    # Bulk attendance marking
    students = StudentProfile.objects.select_related('user').all()
    context = {'students': students, 'today': timezone.now().date()}
    return render(request, 'rewards_app/teacher/mark_attendance.html', context)


@teacher_required
def manage_store(request):
    """Manage store products"""
    products = Product.objects.filter(created_by=request.user).order_by('-created_at')
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
    }
    return render(request, 'rewards_app/teacher/manage_store.html', context)


@teacher_required
def add_product(request):
    """Add new product to store"""
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, _('Product added successfully!'))
            return redirect('rewards_app:manage_store')
    else:
        form = AddProductForm()
    
    return render(request, 'rewards_app/teacher/add_product.html', {'form': form})


@teacher_required
def edit_product(request, product_id):
    """Edit existing product"""
    product = get_object_or_404(Product, pk=product_id, created_by=request.user)
    
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, _('Product updated successfully!'))
            return redirect('rewards_app:manage_store')
    else:
        form = AddProductForm(instance=product)
    
    return render(request, 'rewards_app/teacher/edit_product.html', {'form': form, 'product': product})


@teacher_required
@require_POST
def delete_product(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, pk=product_id, created_by=request.user)
    product.delete()
    messages.success(request, _('Product deleted successfully!'))
    return redirect('rewards_app:manage_store')


@teacher_required
def collections(request):
    """View all students' collections (purchased products)"""
    # Get all orders with related student and product
    all_orders = Order.objects.select_related('student', 'product').order_by('-created_at')
    
    # Get students and their collection counts
    students = StudentProfile.objects.annotate(
        collection_count=Count('orders')
    ).order_by('-collection_count')
    
    # Filter by student if specified
    student_filter = request.GET.get('student')
    if student_filter:
        all_orders = all_orders.filter(student_id=student_filter)
    
    # Pagination
    paginator = Paginator(all_orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
        'students': students,
        'selected_student': student_filter,
    }
    return render(request, 'rewards_app/teacher/collections.html', context)


# ============================================================================
# STUDENT VIEWS
# ============================================================================

@student_required
def student_dashboard(request):
    """Student main dashboard"""
    student = request.user.student_profile
    recent_transactions = student.transactions.all().order_by('-created_at')[:10]
    recent_attendances = student.attendances.all().order_by('-date')[:10]
    recent_collections = student.orders.select_related('product').order_by('-created_at')[:6]
    
    context = {
        'student': student,
        'recent_transactions': recent_transactions,
        'recent_attendances': recent_attendances,
        'recent_collections': recent_collections,
    }
    return render(request, 'rewards_app/student/dashboard.html', context)


@student_required
def student_ranking(request):
    """View leaderboard/ranking"""
    # Get all students ranked by coins and attendance
    rankings = StudentProfile.objects.all().order_by('-total_coins', '-attendance_count')
    
    # Find student's position
    student = request.user.student_profile
    student_rank = rankings.filter(
        Q(total_coins__gt=student.total_coins) |
        (Q(total_coins=student.total_coins) & Q(attendance_count__gt=student.attendance_count))
    ).count() + 1
    
    paginator = Paginator(rankings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'rankings': page_obj.object_list,
        'student_rank': student_rank,
        'all_rankings': rankings,
    }
    return render(request, 'rewards_app/student/ranking.html', context)


@student_required
def view_attendance(request):
    """View student's attendance history"""
    student = request.user.student_profile
    attendances = student.attendances.all().order_by('-date')
    
    # Calculate attendance statistics
    total_records = attendances.count()
    present_count = attendances.filter(status=AttendanceStatus.PRESENT).count()
    absent_count = attendances.filter(status=AttendanceStatus.ABSENT).count()
    attendance_percentage = (present_count / total_records * 100) if total_records > 0 else 0
    
    paginator = Paginator(attendances, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'attendances': page_obj.object_list,
        'attendance_percentage': attendance_percentage,
        'present_count': present_count,
        'absent_count': absent_count,
        'total_records': total_records,
    }
    return render(request, 'rewards_app/student/attendance.html', context)


@student_required
def transaction_history(request):
    """View transaction history"""
    student = request.user.student_profile
    transactions = student.transactions.all().order_by('-created_at')
    
    paginator = Paginator(transactions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'transactions': page_obj.object_list,
    }
    return render(request, 'rewards_app/student/transaction_history.html', context)


@student_required
def browse_store(request):
    """Browse available products in the store"""
    products = Product.objects.filter(is_active=True, quantity_available__gte=-1).order_by('-created_at')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
    }
    return render(request, 'rewards_app/student/store.html', context)


@student_required
@require_POST
def purchase_product(request, product_id):
    """Purchase product from store"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    student = request.user.student_profile
    quantity = int(request.POST.get('quantity', 1))
    
    # Validate quantity
    if quantity < 1:
        messages.error(request, _('Invalid quantity.'))
        return redirect('rewards_app:browse_store')
    
    # Check availability
    if not product.is_available():
        messages.error(request, _('This product is not available.'))
        return redirect('rewards_app:browse_store')
    
    # Calculate total cost
    total_cost = product.price * quantity
    
    # Check if student has enough coins
    if student.total_coins < total_cost:
        messages.error(
            request,
            _('You do not have enough coins. You need %(needed)d coins.') % {
                'needed': total_cost - student.total_coins
            }
        )
        return redirect('rewards_app:browse_store')
    
    # Create order
    order = Order.objects.create(
        student=student,
        product=product,
        coins_spent=total_cost,
        quantity=quantity
    )
    
    # Update student coins and product quantity
    student.spend_coins(total_cost)
    product.decrease_quantity()
    
    # Create transaction record
    Transaction.objects.create(
        student=student,
        coins=total_cost,
        transaction_type=TransactionType.SPEND,
        reason=_('Purchased: %(product)s x%(quantity)d') % {
            'product': product.name,
            'quantity': quantity
        },
        created_by=None
    )
    
    messages.success(
        request,
        _('Purchase successful! %(product)s x%(quantity)d added to your collection.') % {
            'product': product.name,
            'quantity': quantity
        }
    )
    return redirect('rewards_app:student_dashboard')


@student_required
def student_purchases(request):
    """View student's purchase history"""
    student = request.user.student_profile
    orders = student.orders.select_related('product').order_by('-created_at')
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
    }
    return render(request, 'rewards_app/student/purchase_history.html', context)


# ============================================================================
# API ENDPOINTS (JSON responders)
# ============================================================================

@teacher_required
def api_student_stats(request, student_id):
    """Get student statistics as JSON"""
    student = get_object_or_404(StudentProfile, pk=student_id)
    
    return JsonResponse({
        'name': student.user.get_full_name(),
        'coins': student.total_coins,
        'attendance': student.attendance_count,
        'rank': student.rank,
        'total_transactions': student.transactions.count(),
        'total_orders': student.orders.count(),
    })


@login_required
def api_leaderboard(request):
    """Get top 10 students as JSON"""
    top_students = StudentProfile.objects.all().order_by('-total_coins', '-attendance_count')[:10]
    
    data = [
        {
            'rank': idx + 1,
            'name': student.user.get_full_name(),
            'coins': student.total_coins,
            'attendance': student.attendance_count,
        }
        for idx, student in enumerate(top_students)
    ]
    
    return JsonResponse({'leaderboard': data})


# ============================================================================
# USER PROFILE VIEW
# ============================================================================

@login_required
def profile(request):
    """View and edit user profile"""
    user = request.user
    student_profile = None
    
    # Get student profile if user is a student
    if user.role == 'student':
        try:
            student_profile = user.student_profile
        except StudentProfile.DoesNotExist:
            student_profile = None
    
    context = {
        'user': user,
        'student_profile': student_profile,
        'is_student': user.role == 'student',
        'is_teacher': user.role == 'teacher',
    }
    return render(request, 'rewards_app/profile.html', context)
