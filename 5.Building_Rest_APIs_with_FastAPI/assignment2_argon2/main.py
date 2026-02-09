"""
Advanced Todo List API - Complete Implementation
All-in-one file for maximum simplicity
"""
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from datetime import datetime, timedelta
from typing import Optional, List
import enum
import secrets
import string
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================================
# CONFIGURATION
# ============================================================================
DATABASE_URL = "sqlite:///./todo.db"
SECRET_KEY = "your-secret-key-change-in-production-must-be-at-least-32-characters-long"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Email settings (optional)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
FROM_EMAIL = "noreply@todoapp.com"

# ============================================================================
# DATABASE SETUP
# ============================================================================
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# ENUMS
# ============================================================================
class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# ============================================================================
# DATABASE MODELS
# ============================================================================
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    receive_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assigned_tasks = relationship("Task", back_populates="assigned_user", foreign_keys="Task.assigned_to_id")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by_id")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    description = Column(Text, nullable=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    is_admin_assigned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by_id])
    assigned_user = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to_id])

# Create tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    role: UserRole
    is_email_verified: bool
    receive_notifications: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TaskCreate(BaseModel):
    assigned_to_id: int
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_by_id: int
    assigned_to_id: int
    name: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    priority: TaskPriority
    status: TaskStatus
    is_admin_assigned: bool
    created_at: datetime
    updated_at: datetime

# ============================================================================
# PASSWORD HASHING (ARGON2)
# ============================================================================
ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash password using Argon2"""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, Exception):
        return False

# ============================================================================
# JWT AUTHENTICATION
# ============================================================================
security = HTTPBearer()

def create_access_token(data: dict) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[str]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    email = decode_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ============================================================================
# EMAIL FUNCTIONS
# ============================================================================
async def send_email(to_email: str, subject: str, body: str):
    """Send email notification"""
    try:
        message = MIMEMultipart()
        message["From"] = FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        
        async with aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT) as smtp:
            await smtp.login(SMTP_USER, SMTP_PASSWORD)
            await smtp.send_message(message)
    except Exception as e:
        print(f"Email error: {e}")

async def notify_task_assigned(user_email: str, task_name: str, admin_email: str):
    """Notify user of task assignment"""
    subject = f"New Task Assigned: {task_name}"
    body = f"""
    <html>
    <body>
        <h2>New Task Assigned</h2>
        <p>Hi {user_email},</p>
        <p>Admin {admin_email} has assigned you a new task: <strong>{task_name}</strong></p>
        <p>Please log in to view details.</p>
    </body>
    </html>
    """
    await send_email(user_email, subject, body)

async def notify_task_completed(admin_email: str, task_name: str, user_email: str):
    """Notify admin of task completion"""
    subject = f"Task Completed: {task_name}"
    body = f"""
    <html>
    <body>
        <h2>Task Completed</h2>
        <p>Hi {admin_email},</p>
        <p>User {user_email} has completed the task: <strong>{task_name}</strong></p>
    </body>
    </html>
    """
    await send_email(admin_email, subject, body)

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(title="Advanced Todo List API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================
@app.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user or admin"""
    # Check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
        email_verification_token=''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/verify-email")
async def verify_email(email: EmailStr, token: str, db: Session = Depends(get_db)):
    """Verify email"""
    user = db.query(User).filter(User.email == email).first()
    if not user or user.email_verification_token != token:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user.is_email_verified = True
    user.email_verification_token = None
    db.commit()
    
    return {"message": "Email verified"}

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================
@app.post("/admin/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create and assign task (Admin only)"""
    # Check user exists
    assigned_user = db.query(User).filter(User.id == task.assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate dates
    if task.end_date <= task.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Create task
    start_date = task.start_date.replace(tzinfo=None)
    end_date = task.end_date.replace(tzinfo=None)

    db_task = Task(
    created_by_id=admin.id,
    assigned_to_id=task.assigned_to_id,
    name=task.name,
    description=task.description,
    start_date=start_date,
    end_date=end_date,
    priority=task.priority,
    status=task.status,
    is_admin_assigned=True
)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Send notification
    if assigned_user.receive_notifications:
        try:
            await notify_task_assigned(assigned_user.email, task.name, admin.email)
        except:
            pass
    
    return db_task

@app.get("/admin/tasks", response_model=List[TaskResponse])
async def get_all_tasks(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all tasks (Admin only)"""
    return db.query(Task).offset(skip).limit(limit).all()

@app.put("/admin/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update task (Admin only)"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return task

@app.delete("/admin/tasks/{task_id}")
async def delete_task(
    task_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete task (Admin only)"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted"}

# ============================================================================
# USER ENDPOINTS
# ============================================================================
@app.get("/user/tasks", response_model=List[TaskResponse])
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get my assigned tasks"""
    return db.query(Task).filter(Task.assigned_to_id == current_user.id).all()

@app.get("/user/tasks/{task_id}", response_model=TaskResponse)
async def get_task_details(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task details"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@app.put("/user/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark task as completed"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.is_admin_assigned and task.status == TaskStatus.CANCELLED:
        raise HTTPException(status_code=403, detail="Cannot cancel admin-assigned tasks")
    
    task.status = TaskStatus.COMPLETED
    task.updated_at = datetime.utcnow()
    db.commit()
    
    # Notify admin
    admin = db.query(User).filter(User.id == task.created_by_id).first()
    if admin and admin.receive_notifications:
        try:
            await notify_task_completed(admin.email, task.name, current_user.email)
        except:
            pass
    
    return {"message": "Task completed"}

@app.put("/user/notifications")
async def update_notifications(
    receive_notifications: bool = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences"""
    current_user.receive_notifications = receive_notifications
    db.commit()
    
    return {"message": f"Notifications {'enabled' if receive_notifications else 'disabled'}"}

@app.post("/user/unsubscribe")
async def unsubscribe(email: EmailStr, db: Session = Depends(get_db)):
    """Unsubscribe from notifications"""
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.receive_notifications = False
        db.commit()
    
    return {"message": "Unsubscribed"}

# ============================================================================
# HEALTH CHECK
# ============================================================================
@app.get("/")
async def root():
    """Health check"""
    return {
        "message": "Advanced Todo List API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

# ============================================================================
# RUN SERVER
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
