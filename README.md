# CollabSpace

CollabSpace is a modern web application built with Django designed to connect university students for Final Year Projects (FYPs) and Paid Tasks based on skills and expertise. It features a premium dashboard UI, a bento-box home page, a skill-matching system, and built-in AI assistance for creating project posts.

## Features

- **Smart Team Matching**: Find teammates based on precise skill sets like Python, React, and Machine Learning.
- **Paid Task Board**: Discover and post paid gigs for your peers to work on.
- **Rich Profiles**: Showcase your tech stack, GitHub link, and proficiency levels.
- **AI-Powered Assistance**: Auto-generate compelling task titles and descriptions using built-in AI.
- **Premium UI/UX**: Designed with a stunning, modern glassmorphism aesthetic and dynamic animations.

---

## Prerequisites

Before you begin, ensure you have the following installed on your machine:
- [Python 3.x](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

---

## Getting Started

Follow these steps to set up the project locally:

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd CollabSpace
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
- **On Windows:**
  ```powershell
  .\venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies
Install all required packages from the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations
Set up the SQLite database by running the migration commands.
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser
Create an admin account to manage the application from the Django admin interface.
```bash
python manage.py createsuperuser
```
*(Follow the prompts to set your username, email, and password)*

### 7. Run the Development Server
Start the local server to run the web application.
```bash
python manage.py runserver
```

Once the server is running, you can access the website by navigating to `http://127.0.0.1:8000/` in your web browser. You can access the admin panel at `http://127.0.0.1:8000/admin/`.

---

## Contributing
Feel free to open issues or submit pull requests if you want to contribute to CollabSpace!
