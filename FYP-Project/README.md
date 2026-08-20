# CollabSpace

CollabSpace is a modern, modular Django web application designed to connect university students for **Final Year Projects (FYPs)** and **Paid Tasks** based on skills, academic programs, and expertise.

It features a clean domain-driven architecture, a skill-matching system, student senior directory, real-time messaging, and built-in AI assistance for creating project posts.

---

## Key Features

- **Smart Team Matching**: Find teammates based on precise skill sets (e.g. Python, React, Machine Learning, Django).
- **Paid Task Board**: Discover and post paid tasks/gigs for peers to work on.
- **Senior Directory**: Connect with senior students (Semesters 6, 7 & 8) for guidance and project collaboration.
- **Direct Messaging & Blocking**: Peer-to-peer real-time chat with inbox unread counters and blocking controls.
- **AI-Powered Assistance**: Auto-generate compelling task titles and descriptions using built-in AI suggesters and an interactive chatbot assistant.
- **Modular Django Architecture**: Cleanly separated Django apps (`accounts`, `posts`, `messaging`, `assistant`, `pages`) with namespaced templates.

---

## File & Directory Structure

The project follows a clean domain-driven Django structure:

```text
FYP_Project/
│
├── collabspace/              # Project Configuration Package
│   ├── settings.py           # Main settings (Installed apps, middleware, DB configuration)
│   ├── urls.py               # Root URL router incorporating all app URL modules
│   ├── wsgi.py               # WSGI server entry point for deployment
│   └── asgi.py               # ASGI server entry point for async compatibility
│
├── accounts/                 # Accounts & User Profiles App
│   ├── models.py             # Models: Profile, Skill, UserSkill
│   ├── views.py              # Auth (register, login, logout), profile edit, skill manager, senior directory
│   ├── urls.py               # URL routing for authentication, profiles, and seniors
│   └── admin.py              # Admin panel registrations for user profile models
│
├── posts/                    # Project & Paid Tasks Management App
│   ├── models.py             # Model: Post (FYP / Paid Tasks with skills & deadlines)
│   ├── forms.py              # PostForm model form with custom widgets
│   ├── views.py              # Views: tasks feed, add post, edit post, delete post, my posts
│   ├── urls.py               # URL routing for post management and task feed
│   └── admin.py              # Admin panel registration for posts
│
├── messaging/                # Real-Time Chat & User Blocking App
│   ├── models.py             # Models: Message, Block
│   ├── views.py              # Views: inbox, chat room, send message, toggle block
│   ├── context_processors.py # Context processor for live unread message counts
│   ├── urls.py               # URL routing for messaging and block actions
│   └── admin.py              # Admin panel registration for messages and block records
│
├── assistant/                # AI Services & Chatbot App
│   ├── views.py              # API views: ai_suggest (title/description generator), chatbot assistant endpoint
│   └── urls.py               # API endpoints for AI suggest (/api/ai-suggest/) and chatbot (/api/chatbot/)
│
├── pages/                    # Landing & Global Context App
│   ├── views.py              # View: home (bento-box landing page)
│   ├── context_processors.py # Context processor for global post creation modal
│   └── urls.py               # Root URL route for home page (/)
│
├── templates/                # Domain-Namespaced HTML Templates
│   ├── pages/                # Landing & base templates (base.html, home.html)
│   ├── accounts/             # Auth & Profile templates (login.html, register.html, profile.html, add_skills.html, seniors.html)
│   ├── posts/                # Post templates (tasks.html, add_post.html, my_posts.html)
│   └── messaging/            # Chat templates (chat.html, messages_inbox.html)
│
├── static/                   # Static CSS & JS Assets
│   ├── css/                  # CSS stylesheets (base.css, auth.css, home.css)
│   └── js/                   # Frontend scripts (base.js, auth.js)
│
├── add_more_skills.py        # Script to pre-populate database with default tech skills
├── manage.py                 # Django command-line utility
├── requirements.txt          # Python project dependencies
└── db.sqlite3                # SQLite database file
```

---

## Detailed Component Responsibilities

| File / App | Description & Functionality |
| :--- | :--- |
| **`collabspace/settings.py`** | Configures installed apps (`accounts`, `posts`, `messaging`, `assistant`, `pages`), middleware, database settings, and global context processors. |
| **`collabspace/urls.py`** | Connects root paths to app-level `urls.py` files and serves static/media files in development. |
| **`accounts/models.py`** | Defines `Profile` (department, program, semester, bio, links), `Skill` (category, name), and `UserSkill` (user skill mapping). |
| **`accounts/views.py`** | Handles user registration, login, logout, profile rendering, skill updating, and senior student filtering. |
| **`posts/models.py`** | Defines `Post` model with post type (`fyp` or `paid`), description, required skills, and deadline. |
| **`posts/views.py`** | Handles listing available tasks, filtering posts by skill/type, creating new posts, editing, and deletion. |
| **`messaging/models.py`** | Defines `Message` (sender, receiver, content, timestamps) and `Block` (blocker, blocked). |
| **`messaging/views.py`** | Renders user inbox, manages chat conversations, handles message delivery, and enforces blocking rules. |
| **`assistant/views.py`** | Provides JSON endpoints for AI project title/description suggestions and interactive chatbot query responses. |
| **`pages/views.py`** | Renders the public landing page showcasing platform features and steps. |
| **`add_more_skills.py`** | Utility script to bulk add programming, framework, database, and AI skills into the database. |

---

## Prerequisites

Before running the application, ensure you have installed:
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

---

## How to Clone and Run the Project

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd FYP_Project
```

### 2. Create and Activate Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Populate Default Skills (Optional)
Run the helper script to add technical skills:
```bash
python add_more_skills.py
```

### 6. Create an Admin / Superuser
```bash
python manage.py createsuperuser
```
*(Follow the prompts to enter your username, email, and password)*

### 7. Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Application**: `http://127.0.0.1:8000/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`
