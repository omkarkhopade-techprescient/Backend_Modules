import os
from datetime import timedelta

# Database Configuration
DATABASE_URL = "sqlite:///./test.db"

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Application Configuration
APP_NAME = "Todo List API"
APP_VERSION = "1.0.0"

# Task Status Options
TASK_STATUS_OPTIONS = ["pending", "in_progress", "completed", "cancelled"]

# Task Priority Options
TASK_PRIORITY_OPTIONS = ["low", "medium", "high"]
