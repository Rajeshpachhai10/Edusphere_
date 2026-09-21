# 🎓 EduSphere

A full-stack online learning platform built with Django and Bootstrap 5 — course management, enrollment and progress tracking, self-service quizzes, discussion forums, real payment gateway integration, and a custom admin dashboard, all in one project.

## 🌐 Live Demo

🔗 [myedusphere.pythonanywhere.com](https://myedusphere.pythonanywhere.com)

## 📌 About the Project

EduSphere was built to satisfy a real-world brief: an online learning platform with user authentication, multimedia course content, enrollment and progress tracking with quizzes, discussion forums, payment integration, and an admin dashboard for managing courses, students, instructors, and payments.

Every item in the brief is built and live. Beyond that, the project also includes a fully self-service instructor quiz builder (no admin access needed), a custom admin oversight dashboard alongside Django's built-in admin, and persistent cloud media storage for course thumbnails.

## ✨ Features

### Authentication & Roles
- 🔐 **Custom Authentication** — Email-based `CustomUser` model with student, instructor, and admin roles, each with its own registration flow
- 🧭 **Role-Aware Navigation** — "My Courses" and "Dashboard" links shown only to the roles that need them

### Course Management
- 📚 **Content Hierarchy** — Category → Course → Module → Lesson structure, with video, PDF, and text lesson types
- 🖥️ **Instructor Dashboard** — Instructors see and manage only their own courses (object-level permission via queryset filtering)
- 🌐 **Public Catalog** — Searchable, filterable course catalog with an accordion-style module preview on each course page
- 🖼️ **Persistent Media** — Course thumbnails stored on Cloudinary (survives redeploys, unlike local disk storage)
- 🔗 **Safe Slugs** — Automatic slug de-duplication on Course and Category creation (no more `UNIQUE constraint failed` on repeated titles)

### Enrollment & Progress
- ✅ **Enrollment Tracking** — Students enroll in courses (free or paid), with a `LessonProgress` model tracking completion lesson-by-lesson
- ▶️ **Resume Where You Left Off** — "Continue" always routes to the correct next lesson, never back to the sales page
- 📊 **Computed Progress** — Course-level progress percentage calculated from lesson completion

### Quizzes
- 📝 **Auto-Grading** — Quiz, Question, Choice, QuizAttempt, and StudentAnswer models with automatic scoring
- 🛠️ **Fully Self-Service Instructor Builder** — Instructors create quizzes, add questions, and add choices entirely from the site — no Django admin access required
- ✅ **Validated Choices** — Server-side validation guarantees exactly one correct choice and at least two filled-in choices per question
- 🔗 **Discoverable Everywhere** — Quiz links appear both on the course page and in the lesson sidebar

### Discussion Forums
- 💬 **Course-Scoped Threads** — Students and instructors discuss per-course (not per-lesson), with thread creation, listing, and replies
- 🔗 **Sidebar Access** — A course-wide "Course Discussions" link is always visible while working through lessons

### Payments
- 💳 **eSewa Integration** — Real sandbox payment flow (rc-epay), chosen to match the HMAC-SHA256 signature method taught in-class
- 🔒 **Hardened Verification** — `hmac.compare_digest()` signature checks, `Decimal`-based amount comparison (not fragile string matching), ownership checks, and `transaction.atomic()` around order completion + enrollment
- 🧾 **Order Lifecycle** — Orders move through pending → completed → failed, deduplicated by a unique `transaction_uuid`
- 🚪 **Payment-Gated Enrollment** — Paid courses require a verified payment before enrollment is created; free courses are unaffected

### Admin Dashboard
- 🛠️ **Custom Oversight Views** — A dedicated `dashboard` app (admin-only, 403-protected) covering all four areas from the brief:
  - 📈 Overview stats (aggregate counts, revenue in रु.)
  - 📚 Course oversight — search, publish-status filter
  - 👥 User management — search, role filter, activate/deactivate (with self-lockout and admin-exclusion guards)
  - 💰 Payment oversight — status filter, manual "Mark as Failed" for stuck pending orders
- 🗂️ **Django Admin Retained** — Standard Django admin still available as the CRUD safety net for individual models


## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 6.0.6 |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Database | SQLite |
| Media Storage | Cloudinary |
| Payments | eSewa (sandbox, rc-epay) |
| Deployment | PythonAnywhere |

## 🗂️ Project Structure

| App | Responsibility |
|---|---|
| `accounts` | Custom user model, authentication, roles |
| `courses` | Category/Course/Module/Lesson models and views |
| `enrollments` | Enrollment and lesson progress tracking |
| `quizzes` | Quiz, question, and choice models, auto-grading, self-service instructor quiz builder |
| `forums` | Course-scoped discussion threads |
| `payments` | eSewa payment integration, signature verification, Order lifecycle |
| `dashboard` | Admin-only oversight views (courses, users, payments, stats) |

## ⚙️ Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/Rajeshpachhai10/Edusphere.git
cd Edusphere

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
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
ESEWA_SECRET_KEY=your-esewa-secret
ESEWA_PRODUCT_CODE=your-esewa-product-code
ESEWA_FORM_URL=your-esewa-form-url
ESEWA_STATUS_CHECK_URL=your-esewa-status-check-url
```

## 🚀 Deployment

Currently deployed on [PythonAnywhere](https://www.pythonanywhere.com) using SQLite for the database, with Cloudinary handling persistent media storage (course thumbnails) and static files served via PythonAnywhere's static file mappings.


## 🙋 Author

**Rajesh Bahadur Pachhai**
GitHub: [@Rajeshpachhai10](https://github.com/Rajeshpachhai10)
Live Site: [myedusphere.pythonanywhere.com](https://myedusphere.pythonanywhere.com)

## 📄 License

This project is open source and available under the MIT License.
