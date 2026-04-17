"""
URL Configuration for rewards_app
"""

from django.urls import path
from . import views

app_name = 'rewards_app'

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/students/', views.manage_students, name='manage_students'),
    path('teacher/students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('teacher/students/add/', views.add_student, name='add_student'),
    path('teacher/students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('teacher/reward/', views.reward_student, name='reward_student'),
    path('teacher/attendance/', views.mark_attendance, name='mark_attendance'),
    path('teacher/store/', views.manage_store, name='manage_store'),
    path('teacher/store/add/', views.add_product, name='add_product'),
    path('teacher/store/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('teacher/store/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('teacher/collections/', views.collections, name='collections'),
    
    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/ranking/', views.student_ranking, name='student_ranking'),
    path('student/attendance/', views.view_attendance, name='view_attendance'),
    path('student/transactions/', views.transaction_history, name='transaction_history'),
    path('student/store/', views.browse_store, name='browse_store'),
    path('student/store/<int:product_id>/purchase/', views.purchase_product, name='purchase_product'),
    path('student/purchases/', views.student_purchases, name='student_purchases'),
    
    # API URLs
    path('api/student/<int:student_id>/stats/', views.api_student_stats, name='api_student_stats'),
    path('api/leaderboard/', views.api_leaderboard, name='api_leaderboard'),
]
