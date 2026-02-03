from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from assignment2_database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    oauth_provider = Column(String, nullable=True)  # 'google', 'github', etc.
    oauth_id = Column(String, nullable=True)
    receive_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tasks = relationship("Task", back_populates="assigned_to", foreign_keys="Task.assigned_to_id")
    created_tasks = relationship("Task", back_populates="created_by_user", foreign_keys="Task.created_by_id")
    notifications = relationship("EmailNotificationLog", back_populates="user")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), index=True)  # Admin who created it
    assigned_to_id = Column(Integer, ForeignKey("users.id"), index=True)  # User task is assigned to
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    is_admin_assigned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by_user = relationship("User", back_populates="created_tasks", foreign_keys=[created_by_id])
    assigned_to = relationship("User", back_populates="tasks", foreign_keys=[assigned_to_id])


class EmailNotificationLog(Base):
    __tablename__ = "email_notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    notification_type = Column(String)  # 'task_assigned', 'task_completed'
    recipient_email = Column(String)
    subject = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)
    sent_successfully = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="notifications")
