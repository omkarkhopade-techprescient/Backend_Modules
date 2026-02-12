# Advanced Todo List API

A production-ready FastAPI application with proper project structure, environment variable management, and role-based access control.

## 🏗️ Project Structure

```
todo_api_restructured/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py                 # Main API router
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── admin.py           # Admin endpoints
│   │       └── user.py            # User endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings using pydantic-settings
│   │   ├── security.py            # Password hashing (Argon2)
│   │   └── auth.py                # JWT authentication
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base_class.py          # SQLAlchemy Base
│   │   ├── session.py             # Database session
│   │   └── init_db.py             # Database initialization
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User model
│   │   └── task.py                # Task model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                # User Pydantic schemas
│   │   └── task.py                # Task Pydantic schemas
│   └── services/
│       ├── __init__.py
│       └── email.py               # Email notification service
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## ✨ Features

### Security Best Practices
- ✅ **No hardcoded secrets** - All sensitive data in `.env` file
- ✅ **Environment variables** - Using `python-dotenv` and `pydantic-settings`
- ✅ **Argon2 password hashing** - Modern, secure password hashing
- ✅ **JWT authentication** - Stateless authentication
- ✅ **Role-based access control** - Admin and User roles

### Application Features
- ✅ User/Admin registration with email verification
- ✅ JWT-based authentication
- ✅ Admin: Create, view, update, delete all tasks
- ✅ Users: View assigned tasks, mark as complete
- ✅ Email notifications (task assignment & completion)
- ✅ Notification preferences (subscribe/unsubscribe)

### Code Quality
- ✅ **Modular structure** - Following FastAPI best practices
- ✅ **Separation of concerns** - Models, schemas, services separated
- ✅ **Type hints** - Full type annotation
- ✅ **Docstrings** - Comprehensive documentation
- ✅ **Git-safe** - Secrets excluded via .gitignore

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
cd todo_api_restructured

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required environment variables:**

```env
# Database
DATABASE_URL=sqlite:///./todo.db

# Security - GENERATE A STRONG SECRET KEY!
SECRET_KEY=use-openssl-rand-hex-32-to-generate-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=noreply@todoapp.com
```

### 3. Generate Secret Key

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Or using OpenSSL
openssl rand -hex 32
```

Copy the output and paste it as `SECRET_KEY` in your `.env` file.

### 4. Run the Application

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "role": "USER"  # or "ADMIN"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### Verify Email
```http
POST /api/auth/verify-email?email=user@example.com&token=verification_token
```

### Admin Endpoints

**All admin endpoints require `Authorization: Bearer <token>` header**

#### Create Task
```http
POST /api/admin/tasks
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "assigned_to_id": 2,
  "name": "Complete documentation",
  "description": "Write comprehensive API docs",
  "priority": "high",
  "status": "pending"
}
```

#### Get All Tasks
```http
GET /api/admin/tasks?skip=0&limit=100
Authorization: Bearer <admin_token>
```

#### Update Task
```http
PUT /api/admin/tasks/{task_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "status": "completed",
  "priority": "low"
}
```

#### Delete Task
```http
DELETE /api/admin/tasks/{task_id}
Authorization: Bearer <admin_token>
```

### User Endpoints

**All user endpoints require `Authorization: Bearer <token>` header**

#### Get My Tasks
```http
GET /api/user/tasks
Authorization: Bearer <user_token>
```

#### Get Task Details
```http
GET /api/user/tasks/{task_id}
Authorization: Bearer <user_token>
```

#### Complete Task
```http
PUT /api/user/tasks/{task_id}/complete
Authorization: Bearer <user_token>
```

#### Update Notification Preferences
```http
PUT /api/user/notifications
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "receive_notifications": false
}
```

#### Unsubscribe
```http
POST /api/user/unsubscribe?email=user@example.com
```

## 🔐 Security

### Environment Variables

**NEVER commit `.env` file to git!**

The `.gitignore` file is configured to exclude:
- `.env` (contains secrets)
- `*.db` (SQLite databases)
- `__pycache__/` (Python cache)
- Virtual environments

### Password Security

- Uses **Argon2** (modern, recommended by OWASP)
- Minimum 8 characters enforced
- Passwords are never stored in plain text

### JWT Tokens

- Configurable expiration (default 30 minutes)
- HS256 algorithm
- Secret key loaded from environment

## 📧 Email Configuration

### Gmail Setup

1. Enable 2-factor authentication
2. Generate App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the generated password
3. Update `.env`:
   ```env
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=generated-app-password
   ```

### Other SMTP Providers

Update `.env` accordingly:
```env
SMTP_SERVER=smtp.your-provider.com
SMTP_PORT=587  # or 465 for SSL
SMTP_USER=your-email
SMTP_PASSWORD=your-password
```

## 🗄️ Database

### SQLite (Default)
```env
DATABASE_URL=sqlite:///./todo.db
```

### PostgreSQL
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### MySQL
```env
DATABASE_URL=mysql://user:password@localhost/dbname
```

## 🧪 Testing

### Manual Testing

1. **Register Admin:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "adminpass123",
    "role": "ADMIN"
  }'
```

2. **Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "adminpass123"
  }'
```

3. **Use Token:**
```bash
TOKEN="your-token-here"

curl -X GET "http://localhost:8000/api/admin/tasks" \
  -H "Authorization: Bearer $TOKEN"
```

## 📦 Dependencies

- **fastapi** - Modern web framework
- **uvicorn** - ASGI server
- **sqlalchemy** - SQL toolkit and ORM
- **pydantic** - Data validation
- **pydantic-settings** - Settings management
- **python-dotenv** - Environment variables
- **python-jose** - JWT implementation
- **argon2-cffi** - Password hashing
- **aiosmtplib** - Async SMTP client
- **email-validator** - Email validation

## 🚢 Deployment

### Production Checklist

- [ ] Generate strong `SECRET_KEY` (32+ characters)
- [ ] Set `DEBUG=False` in `.env`
- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Configure CORS for specific origins
- [ ] Set up HTTPS/SSL
- [ ] Configure production SMTP service
- [ ] Set appropriate `ACCESS_TOKEN_EXPIRE_MINUTES`
- [ ] Enable logging
- [ ] Set up monitoring
- [ ] Regular backups

### Environment-Specific `.env` Files

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production
```

Load appropriate file based on environment.

## 📖 Best Practices Followed

1. ✅ **Separation of Concerns** - Models, schemas, services, endpoints separated
2. ✅ **Environment Variables** - No hardcoded secrets
3. ✅ **Type Hints** - Full type annotation throughout
4. ✅ **Dependency Injection** - FastAPI's dependency system
5. ✅ **Error Handling** - Proper HTTP exceptions
6. ✅ **Documentation** - Docstrings and OpenAPI docs
7. ✅ **Security** - Modern password hashing, JWT auth
8. ✅ **Git Safety** - Proper .gitignore configuration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is provided as-is for educational purposes.

## 🆘 Support

For issues and questions:
- Check the `/docs` endpoint for API documentation
- Review this README
- Check environment variables are set correctly
- Verify database connection

---

**Remember:** Never commit `.env` file or expose your `SECRET_KEY`!
