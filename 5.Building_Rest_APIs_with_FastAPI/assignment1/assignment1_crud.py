from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from assignment1_models import User, Task
from assignment1_schemas import UserCreate, TaskCreate, TaskUpdate
from assignment1_auth import hash_password, verify_password


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user in the database"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError(f"Email {user.email} already registered")
    
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
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
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()


# ==================== Task CRUD ====================

def create_task(db: Session, task: TaskCreate, user_id: int) -> Task:
    """Create a new task for a user"""
    db_task = Task(
        user_id=user_id,
        name=task.name,
        description=task.description,
        start_date=task.start_date,
        end_date=task.end_date,
        priority=task.priority,
        status=task.status
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """Get a specific task by ID (only if owned by user)"""
    return db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()


def get_all_tasks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Task]:
    """Get all tasks for a user with optional filters"""
    query = db.query(Task).filter(Task.user_id == user_id)
    
    # Apply filters
    if priority:
        query = query.filter(Task.priority == priority)
    
    if status:
        query = query.filter(Task.status == status)
    
    if start_date:
        query = query.filter(Task.start_date >= start_date)
    
    if end_date:
        query = query.filter(Task.end_date <= end_date)
    
    return query.offset(skip).limit(limit).all()


def update_task(
    db: Session,
    task_id: int,
    user_id: int,
    task_update: TaskUpdate
) -> Optional[Task]:
    """Update a task (only if owned by user)"""
    db_task = get_task(db, task_id, user_id)
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


def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    """Delete a task (only if owned by user)"""
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True
