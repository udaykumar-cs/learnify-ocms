# 🎓 Learnify – Online Course Management System (OCMS)

![Django](https://img.shields.io/badge/Django-6.0-green?style=flat&logo=django)
![DRF](https://img.shields.io/badge/DRF-3.14-red?style=flat&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue?style=flat&logo=postgresql)
![JWT](https://img.shields.io/badge/JWT-Auth-orange?style=flat&logo=json-web-tokens)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

A production-ready **Online Course Management System** built with Django REST Framework, JWT Authentication, and PostgreSQL.

---

## ✨ Features

- **JWT Authentication** with role-based access (Admin, Instructor, Student)
- **Course Management** with categories, modules, lectures
- **Enrollment System** with progress tracking
- **Reviews & Ratings** with auto-calculated averages
- **Dashboard Analytics** for Admin, Instructor, Student
- **Redis Caching** for performance optimization
- **Security**: UUID primary keys, environment variables, CORS

---

## 🛠️ Tech Stack

| Backend | Database | Auth | Caching |
|---------|----------|------|---------|
| Django 6.0, DRF | PostgreSQL 13+ | JWT (SimpleJWT) | Redis |

---

## 🚀 Quick Start

```bash
# Clone repo
git clone https://github.com/udaykumar-cs/learnify-ocms.git
cd learnify-ocms

# Virtual environment
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file (see .env.example)
# Setup PostgreSQL database
# Run migrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

📡 Key API Endpoints
Endpoint	Description
/api/token/	Get JWT token
/api/courses/	List/Create courses
/api/enrollments/	Student enrollments
/api/courses/{id}/reviews/	Course reviews
/api/admin/analytics/	Admin dashboard
/api/instructor/dashboard/	Instructor dashboard
/api/student/dashboard/	Student dashboard

👥 User Roles
Role	Capabilities
Admin	Full platform control
Instructor	Create/manage courses
Student	Enroll, learn, review
📝 Environment Variables (.env)

text
SECRET_KEY=your_key
DEBUG=True
DB_NAME=learnify_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

📂 Project Structure
text
learnify/
├── accounts/      # User & auth
├── courses/       # Course models
├── enrollments/   # Enrollment & progress
├── reviews/       # Ratings & feedback
├── dashboard/     # Analytics
├── core/          # Settings
└── templates/     # HTML

👨‍💻 Author
Uday Kumar
📧 kumaruday9973@gmail.com
🐙 @udaykumar-cs

⭐ Support
If this helps, please give it a star on GitHub!

Built with ❤️ by Uday Kumar