# 🎓 EduSphere

A full-stack online learning platform built with Django and Bootstrap 5 — course management, enrollment and progress tracking, quizzes, discussion forums, payments, and an admin dashboard, all in one project.

## 🌐 Live Demo

🔗 [myEdusphere.pythonanywhere.com](https://myEdusphere.pythonanywhere.com)

## 📌 About the Project

EduSphere was built to satisfy a real-world brief: an online learning platform with user authentication, multimedia course content, enrollment and progress tracking with quizzes, discussion forums, payment integration, and an admin dashboard for managing courses, students, instructors, and payments.

Every item in the brief is built and live. Beyond that, the project also includes a fully self-service instructor quiz builder and a custom admin oversight dashboard alongside Django's built-in admin.

## ✨ Features

- 🔐 **Authentication** — Custom email-based user model with student, instructor, and admin roles, each with its own registration flow
- 📚 **Course Management** — Category → Course → Module → Lesson hierarchy, with video, PDF, and text lesson types
- ✅ **Enrollment & Progress Tracking** — Students enroll, track progress lesson-by-lesson, and resume exactly where they left off
- 📝 **Quizzes** — Auto-graded quizzes with a full instructor-facing builder (create quiz, add questions, add choices) — no admin access needed
- 💬 **Discussion Forums** — Course-scoped threads and replies
- 💳 **Payments** — eSewa integration with HMAC-SHA256 signature verification, gating enrollment in paid courses
- 🛠️ **Admin Dashboard** — Custom oversight views for course, student, instructor, and payment management, alongside standard Django admin
- 📱 **Responsive UI** — Bootstrap 5 with a custom ink-blue and amber design system

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 6.0.6 |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Database | SQLite |
| Media Storage | Local filesystem |
| Payments | eSewa (sandbox) |
| Deployment | PythonAnywhere |

## 🗂️ Project Structure

| App | Responsibility |
|---|---|
| `accounts` | Custom user model, authentication, roles |
| `courses` | Category/Course/Module/Lesson models and views |
| `enrollments` | Enrollment and lesson progress tracking |
| `quizzes` | Quiz, question, and auto-grading logic |
| `forums` | Course-scoped discussion threads |
| `payments` | eSewa payment integration |
| `dashboard` | Admin-only oversight views |

## ⚙️ Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/Rajeshpachhai10/Edusphere_.git
cd Edusphere_

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables (see below)

# 5. Apply migrations
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. Run the server
python manage.py runserver
```

Visit → http://127.0.0.1:8000

### Environment Variables

Managed via [python-decouple](https://pypi.org/project/python-decouple/). Create a `.env` file inside the `edusphere/` folder:

```
SECRET_KEY=your-secret-key
DEBUG=True
ESEWA_SECRET_KEY=your-esewa-secret
ESEWA_PRODUCT_CODE=your-esewa-product-code
ESEWA_FORM_URL=your-esewa-form-url
ESEWA_STATUS_CHECK_URL=your-esewa-status-check-url
```

## 🚀 Deployment

Deployed on [PythonAnywhere](https://www.pythonanywhere.com) using SQLite for the database and local filesystem storage for media, with static files served via PythonAnywhere's static file mappings.

## 🙋 Author

**Rajesh Bahadur Pachhai**
GitHub: [@Rajeshpachhai10](https://github.com/Rajeshpachhai10)
Live Site: [myEdusphere.pythonanywhere.com](https://myEdusphere.pythonanywhere.com)

## 📄 License

This project is open source and available under the MIT License.
