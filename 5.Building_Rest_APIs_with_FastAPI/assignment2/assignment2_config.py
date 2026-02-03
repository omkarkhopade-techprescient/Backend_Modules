import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./advanced_todo.db")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@todoapp.com")

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URL = os.getenv("GOOGLE_REDIRECT_URL", "http://localhost:8000/auth/oauth/google/callback")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URL = os.getenv("GITHUB_REDIRECT_URL", "http://localhost:8000/auth/oauth/github/callback")

# Application Configuration
APP_NAME = "Advanced Todo List API"
APP_VERSION = "2.0.0"

# Task Status and Priority Options
TASK_STATUS_OPTIONS = ["pending", "in_progress", "completed", "cancelled"]
TASK_PRIORITY_OPTIONS = ["low", "medium", "high"]

# User Roles
USER_ROLES = ["user", "admin"]
