from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from assignment2_models import User, Task, UserRole, TaskStatus
from assignment2_schemas import UserCreate, TaskCreate, TaskUpdate
from assignment2_auth import hash_password, verify_password, generate_verification_token


# ==================== User CRUD ====================

def create_user(
    db: Session,
    user: UserCreate,
    oauth_provider: Optional[str] = None,
    oauth_id: Optional[str] = None
) -> User:
    """Create a new user in the database"""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError(f"Email {user.email} already registered")
    
    verification_token = generate_verification_token()
    
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password) if user.password else None,
        role=user.role,
        email_verification_token=verification_token,
        is_email_verified=False if not oauth_provider else True,
        oauth_provider=oauth_provider,
        oauth_id=oauth_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if user.hashed_password is None:
        return None  # OAuth user, cannot login with password
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def verify_user_email(db: Session, email: str, token: str) -> bool:
    """Verify user email with token"""
    user = get_user_by_email(db, email)
    if not user:
        return False
    
    if user.email_verification_token != token:
        return False
    
    user.is_email_verified = True
    user.email_verification_token = None
    db.commit()
    return True


def update_user_notifications(db: Session, user_id: int, receive_notifications: bool) -> bool:
    """Update user's notification preference"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.receive_notifications = receive_notifications
    db.commit()
    return True


def create_or_get_oauth_user(
    db: Session,
    email: str,
    oauth_provider: str,
    oauth_id: str,
    role: str = "user"
) -> User:
    """Create or get user authenticated via OAuth"""
    user = get_user_by_email(db, email)
    
    if user:
        # Update OAuth info if not already set
        if not user.oauth_provider:
            user.oauth_provider = oauth_provider
            user.oauth_id = oauth_id
            db.commit()
        return user
    
    # Create new OAuth user
    user_create = UserCreate(email=email, password="", role=role)
    return create_user(
        db,
        user_create,
        oauth_provider=oauth_provider,
        oauth_id=oauth_id
    )


# ==================== Task CRUD ====================

def create_task(db: Session, task: TaskCreate, admin_id: int) -> Task:
    """Create a new task and assign it to a user"""
    db_task = Task(
        created_by_id=admin_id,
        assigned_to_id=task.assigned_to_id,
        name=task.name,
        description=task.description,
        start_date=task.start_date,
        end_date=task.end_date,
        priority=task.priority,
        status=task.status,
        is_admin_assigned=True
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Get a task by ID"""
    return db.query(Task).filter(Task.id == task_id).first()


def get_all_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Task]:
    """Get all tasks with optional filters (Admin only)"""
    query = db.query(Task)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    if status:
        query = query.filter(Task.status == status)
    
    if start_date:
        query = query.filter(Task.start_date >= start_date)
    
    if end_date:
        query = query.filter(Task.end_date <= end_date)
    
    return query.offset(skip).limit(limit).all()


def get_user_tasks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    priority: Optional[str] = None,
    status: Optional[str] = None
) -> List[Task]:
    """Get tasks assigned to a specific user"""
    query = db.query(Task).filter(Task.assigned_to_id == user_id)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    if status:
        query = query.filter(Task.status == status)
    
    return query.offset(skip).limit(limit).all()


def update_task(
    db: Session,
    task_id: int,
    task_update: TaskUpdate
) -> Optional[Task]:
    """Update a task (Admin only)"""
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.utcnow()
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task_status(
    db: Session,
    task_id: int,
    user_id: int,
    new_status: TaskStatus
) -> Optional[Task]:
    """Update task status (User can only update their assigned tasks)"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to_id == user_id
    ).first()
    
    if not db_task:
        return None
    
    # User cannot delete admin-assigned tasks
    if db_task.is_admin_assigned and new_status == TaskStatus.CANCELLED:
        raise ValueError("Cannot delete admin-assigned tasks")
    
    db_task.status = new_status
    db_task.updated_at = datetime.utcnow()
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Delete a task (Admin only)"""
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True


def get_task_creator(db: Session, task_id: int) -> Optional[User]:
    """Get the admin who created the task"""
    task = get_task(db, task_id)
    if not task:
        return None
    return task.created_by_user
