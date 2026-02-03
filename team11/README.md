# Team 11 - Listening & Writing Microservice

## Overview

This microservice provides listening (speaking) and writing assessment functionality for the English learning platform. Users can submit writing texts or audio recordings, receive instant scores (currently static at 90), and view their submission history.

[View Figma Design](https://www.figma.com/design/3uaZuwIjT0OU8v7w2cy7Df/SE1_T11?node-id=0-1&m=dev&t=wTZc2qAKki3quDGV-1)


## Features Implemented (Step 1)

✅ **Database Models**
- `Submission`: Base model for all submissions (writing/listening)
- `WritingSubmission`: Details for writing tasks
- `ListeningSubmission`: Details for listening/speaking tasks
- `AssessmentResult`: Detailed scoring and feedback

✅ **API Endpoints**
- `POST /team11/api/submit-writing/` - Submit writing text
- `POST /team11/api/submit-listening/` - Submit audio recording
- `GET /team11/dashboard/` - View submission history
- `GET /team11/submission/<uuid>/` - View detailed results

✅ **Frontend Pages**
- Landing page with service overview
- Exam type selection page
- Writing exam interface with word counter
- Listening exam interface with audio recording
- Dashboard with submission history
- Detailed results page with scores and feedback

✅ **Static Data (for now)**
- 3 writing topics
- 3 listening topics
- Static score of 90 for all submissions
- Pre-defined feedback and suggestions

## Project Structure

```
team11/
├── models.py              # Database models
├── views.py               # Views and API endpoints
├── urls.py                # URL routing
├── admin.py               # Django admin configuration
├── migrations/            # Database migrations
│   └── 0001_initial.py
├── templates/team11/      # HTML templates
│   ├── index.html         # Landing page
│   ├── start_exam.html    # Exam selection
│   ├── writing_exam.html  # Writing interface
│   ├── listening_exam.html # Audio recording interface
│   ├── dashboard.html     # Submission history
│   └── submission_detail.html # Detailed results
└── static/team11/         # CSS and assets
    ├── styles/
    │   ├── common.css     # Shared styles
    │   └── style.css      # Page-specific styles
    └── public/
        └── images/
```

## How to Run the Project

### Option 1: Local Development (Without Docker)

1. **Ensure Python environment is set up:**
   ```powershell
   # Virtual environment should already be created
   # If not, create it:
   python -m venv .venv
   
   # Activate it (already done by VS Code Python extension)
   .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Verify .env file exists:**
   ```powershell
   # Should already exist from setup
   # If not, copy from example:
   Copy-Item .env.example .env
   ```

4. **Run migrations (already completed):**
   ```powershell
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access):**
   ```powershell
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```powershell
   python manage.py runserver
   ```

7. **Access the application:**
   - Main site: http://localhost:8000/
   - Team 11 microservice: http://localhost:8000/team11/
   - Django admin: http://localhost:8000/admin/

### Option 2: Docker (Production-like)

1. **Create Docker network (if not exists):**
   ```powershell
   docker network create app404_net
   ```

2. **Build and run with Docker Compose:**
   ```powershell
   # From project root
   docker-compose up --build
   ```

3. **Run migrations in Docker:**
   ```powershell
   docker-compose exec core python manage.py migrate
   ```

4. **Create superuser in Docker (optional):**
   ```powershell
   docker-compose exec core python manage.py createsuperuser
   ```

5. **Access the application:**
   - Main site: http://localhost:8000/
   - Team 11 microservice: http://localhost:8000/team11/

## Testing the Microservice

### 1. User Registration and Login

1. Navigate to http://localhost:8000/
2. Click "ثبت نام" (Sign Up) to create an account
3. Fill in the registration form
4. After registration, log in with your credentials

### 2. Test Writing Submission

1. Go to http://localhost:8000/team11/
2. Click "شروع آزمون" (Start Exam)
3. Select a writing topic
4. Write at least 150 words in the text area
5. Click "ارسال و دریافت نمره" (Submit and Get Score)
6. You should receive a score of 90

### 3. Test Listening/Speaking Submission

1. From the exam selection page, choose a listening topic
2. Click "شروع ضبط صدا" (Start Recording)
3. Allow microphone access when prompted
4. Speak for a few seconds
5. Click "توقف ضبط" (Stop Recording)
6. Preview the audio
7. Click "ارسال و دریافت نمره" (Submit and Get Score)
8. You should receive a score of 90

### 4. View Dashboard

1. Click "داشبورد من" (My Dashboard)
2. You should see all your submissions
3. Click "جزئیات" (Details) on any submission to view full results

### 5. Admin Interface (if superuser created)

1. Go to http://localhost:8000/admin/
2. Log in with superuser credentials
3. Navigate to Team11 models to view/manage submissions

## Architecture Notes

- **Microservice Pattern**: Team 11 operates independently with its own database
- **Authentication**: Shared authentication via core app (JWT cookies)
- **Database Router**: Automatically routes team11 models to team11 database
- **Styling**: Matches core project's Persian/RTL design system
- **Static Content**: Currently uses placeholder responses (90 score) for rapid prototyping

## Contributors

Team 11 - Software Engineering Course 1404-01
Amirkabir University of Technology
