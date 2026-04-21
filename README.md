# 🎓 Student Reward System

A Django-based gamification platform designed to motivate and recognize student achievements through a coin-based reward system, attendance tracking, and a virtual store.

## ✨ Features

### 👨‍🏫 For Teachers
- **Dashboard** - Overview of students, coins distributed, and system statistics
- **Student Management** - Add, view, and manage student accounts
- **Reward System** - Award coins to students with custom reasons
- **Attendance Tracking** - Mark individual or bulk attendance (present/absent)
- **Virtual Store** - Create and manage products students can purchase with coins
- **Teacher Approval System** - Admin must approve new teacher registrations
- **Shared Store** - All teachers can view, edit, and delete products (collaborative)

### 👨‍🎓 For Students
- **Dashboard** - View profile, coins, rank, and achievements
- **Ranking System** - Compete based on coins and attendance
- **Store** - Browse and purchase products with earned coins
- **Purchase History** - Track all purchases and collections
- **Attendance Records** - View personal attendance history
- **Leaderboard** - See top performers in the system

### 🌐 General Features
- **Internationalization (i18n)** - Full English and Arabic support with RTL layout
- **Theme System** - Switch between 3 themes (Standard Blue, Warm Brown, Dark Blue)
- **Role-Based Access Control** - Separate views for teachers and students
- **Responsive Design** - Bootstrap 5 for mobile and desktop
- **Database Logging** - Track all transactions and activity
- **Security** - User authentication, role-based permissions, CSRF protection

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd student_reward_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load demo data (optional)**
   ```bash
   python manage.py create_demo_data
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main site: `http://localhost:8000/`
   - Admin panel: `http://localhost:8000/en/secure-admin-panel-2024/`
   - Arabic version: `http://localhost:8000/ar/`

## 📊 Database Models

### CustomUser
- Extends Django's AbstractUser
- Roles: Teacher, Student
- Approval system for teachers
- Fields: username, email, password, role, status, is_approved, created_at, updated_at

### StudentProfile
- Links to CustomUser (one-to-one)
- Tracks: total_coins, attendance_count, rank
- Automatically updated with transactions and attendance

### Transaction
- Logs all coin movements
- Types: reward, spend, adjustment
- Includes: reason, created_by (teacher), timestamp
- Used for audit trail and history

### Attendance
- Marks student presence/absence
- Fields: student, status (present/absent), date, marked_by (teacher), notes
- Used to calculate rankings

### Product
- Virtual store items
- Fields: name, description, price (in coins), image, quantity_available, is_active
- Created by: any teacher (shared store)

### Order
- Student purchase records
- Fields: student, product, quantity, total_coins_spent, created_at
- Used for purchase history and collections

## 🎨 User Interface

### Templates Structure
```
templates/
├── base.html              # Main layout with navigation
├── rewards_app/
│   ├── home.html         # Landing page
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── profile.html      # User profile (read-only)
│   ├── student/          # Student-specific pages
│   │   └── dashboard.html
│   └── teacher/          # Teacher-specific pages
│       ├── dashboard.html
│       ├── manage_students.html
│       ├── mark_attendance.html
│       ├── manage_store.html
│       └── ...
└── registration/         # Django auth templates
```

## 🌍 Internationalization

- **Supported Languages**: English (en), Arabic (ar)
- **Translation File**: `locale/ar/LC_MESSAGES/django.po`
- **RTL Support**: Automatic for Arabic language
- **Theme Integration**: Colors preserved across languages

## 🔐 Security Features

- Hidden admin URL: `/en/secure-admin-panel-2024/` (not `/admin/`)
- User authentication required for most pages
- Role-based access control (teachers vs students)
- CSRF protection on all forms
- Password hashing with Django's security
- Teacher approval system prevents unauthorized access

## 📱 API Endpoints

### Student Statistics (JSON)
```
GET /api/student/<id>/stats/
```

### Leaderboard (JSON)
```
GET /api/leaderboard/
```

## 🛠 Technologies Used

- **Backend**: Django 5.2.7
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Frontend**: Bootstrap 5, jQuery
- **Authentication**: Django's built-in auth system
- **i18n**: Django i18n framework
- **Python**: 3.13.7

## 📁 Project Structure

```
student_reward_system/
├── config/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── rewards_app/         # Main Django app
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── forms.py         # Form classes
│   ├── urls.py          # URL routing
│   ├── admin.py         # Admin interface
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JavaScript
│   └── management/
│       └── commands/
│           └── create_demo_data.py
├── locale/              # Translations (Arabic)
├── manage.py            # Django management
├── requirements.txt     # Python dependencies
└── db.sqlite3          # Database file
```

## 🎯 User Workflows

### For Teachers
1. Register → Await admin approval → Login → Access teacher dashboard
2. Add students to system
3. Award coins for achievements
4. Mark attendance (individual or bulk)
5. Create and manage store products
6. View student statistics and rankings

### For Students
1. Register as student → Login → Access student dashboard
2. View earned coins and rank
3. Browse and purchase products from store
4. View attendance records
5. Check personal achievements
6. See leaderboard rankings

## 🚀 Deployment

### Environment Setup
Create `.env` file with:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=student_reward_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=5432
```

### Production Steps
1. Set `DEBUG=False` in settings
2. Use PostgreSQL instead of SQLite
3. Configure static files collection
4. Use production web server (Gunicorn, uWSGI)
5. Set up reverse proxy (Nginx)
6. Enable HTTPS/SSL
7. Use environment variables for sensitive data

## 📝 Admin Functions

Access admin panel at `/en/secure-admin-panel-2024/`

**Manage:**
- Users (teachers, students, superusers)
- Student profiles and coins
- Transactions and history
- Attendance records
- Products and inventory
- Teacher approvals

## 🐛 Demo Credentials

After running `create_demo_data`:
- **Teacher**: username: `teacher123` / password: `password123`
- **Students**: `student_ahmed`, `student_fatima`, etc. / password: `password123`

## 📋 Requirements

See `requirements.txt`:
- Django 5.2.7
- Python 3.13+
- SQLite or PostgreSQL
- Bootstrap 5 (CDN)
- jQuery (CDN)

## 🎓 Learning Outcomes

This project demonstrates:
- Django MVT (Model-View-Template) architecture
- User authentication and authorization
- Role-based access control
- Database design and ORM
- Internationalization (i18n)
- Form validation and security
- RESTful API basics
- Bootstrap responsive design
- Frontend and backend integration

## 📞 Support

For issues, questions, or suggestions, please:
1. Check the documentation files
2. Review the admin interface
3. Check database for data integrity
4. Verify user roles and permissions

## 📄 License

This project is open source and available under the MIT License.

---

**Created**: April 2026
**Version**: 1.0
**Status**: Complete and Production-Ready
