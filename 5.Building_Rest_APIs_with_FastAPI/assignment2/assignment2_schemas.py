from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from assignment2_models import UserRole, TaskStatus, TaskPriority


# ==================== User Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_email_verified: bool
    receive_notifications: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    receive_notifications: Optional[bool] = None


# ==================== Task Schemas ====================

class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING


class TaskCreate(TaskBase):
    assigned_to_id: int  # Admin assigns task to user


class TaskResponse(TaskBase):
    id: int
    created_by_id: int
    assigned_to_id: int
    is_admin_assigned: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None


# ==================== Auth Schemas ====================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class EmailVerification(BaseModel):
    token: str


# ==================== OAuth Schemas ====================

class GoogleAuthRequest(BaseModel):
    code: str
    role: UserRole = UserRole.USER


class GitHubAuthRequest(BaseModel):
    code: str
    role: UserRole = UserRole.USER


# ==================== Notification Schemas ====================

class NotificationPreference(BaseModel):
    receive_notifications: bool


class UnsubscribeRequest(BaseModel):
    email: EmailStr
    token: str
