from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer , HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

from assignment2_config import (
    APP_NAME, APP_VERSION, ACCESS_TOKEN_EXPIRE_MINUTES
)
from assignment2_database import engine, Base, get_db
from assignment2_models import User, UserRole, TaskStatus
from assignment2_schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    TaskCreate, TaskResponse, TaskUpdate, EmailVerification
)
from assignment2_auth import (
    create_access_token, get_current_user, get_admin_user,
    #authenticate_user
)
from assignment2_crud import (
    create_user, authenticate_user as crud_authenticate_user,
    create_task, get_all_tasks, get_user_tasks, get_task,
    update_task, delete_task, get_task_creator,
    update_task_status, verify_user_email, update_user_notifications
)
from assignment2_email_service import (
    notify_task_assignment, notify_task_completion
)

Base.metadata.create_all(bind=engine) # Create database tables

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Advanced To-Do List API with Admin Features, OAuth, and Email Notifications --by Omkar "
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================== Authentication Endpoints ==================

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (Admin or User)
    Email verification will be required
    """
    try:
        db_user = create_user(db, user)
        # TODO: Send verification email with db_user.email_verification_token
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/auth/verify-email")
async def verify_email(
    verification: EmailVerification,
    email: str,
    db: Session = Depends(get_db)
):
    """
    Verify user email with verification token
    """
    success = verify_user_email(db, email, verification.token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token or email"
        )
    return {"message": "Email verified successfully"}


@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password to get JWT token
    """
    db_user = crud_authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== Admin Task Endpoints ====================

@app.post("/admin/tasks", response_model=TaskResponse)
async def create_admin_task(
    task: TaskCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task and assign it to a user (Admin only)
    """
    # Verify assigned user exists
    assigned_user = db.query(User).filter(User.id == task.assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )
    
    db_task = create_task(db, task, admin.id)
    
    # Send notification email
    await notify_task_assignment(db, db_task, assigned_user, admin)
    
    return db_task


@app.get("/admin/tasks", response_model=List[TaskResponse])
async def get_admin_tasks(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get all tasks (Admin only)
    """
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format"
            )
    
    return get_all_tasks(
        db,
        skip=skip,
        limit=limit,
        priority=priority,
        status=status,
        start_date=start_dt,
        end_date=end_dt
    )


@app.put("/admin/tasks/{task_id}", response_model=TaskResponse)
async def update_admin_task(
    task_id: int,
    task_update: TaskUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a task (Admin only)
    """
    updated_task = update_task(db, task_id, task_update)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return updated_task


@app.delete("/admin/tasks/{task_id}")
async def delete_admin_task(
    task_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task (Admin only)
    """
    success = delete_task(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return {"message": "Task deleted successfully"}


# ==================== User Task Endpoints ====================

@app.get("/user/tasks", response_model=List[TaskResponse])
async def get_user_assigned_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    priority: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get tasks assigned to the current user
    """
    return get_user_tasks(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
        priority=priority,
        status=status
    )


@app.get("/user/tasks/{task_id}", response_model=TaskResponse)
async def get_user_task_details(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific assigned task
    """
    task = get_task(db, task_id)
    if not task or task.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@app.put("/user/tasks/{task_id}/complete")
async def mark_task_complete(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a task as completed
    User cannot delete admin-assigned tasks
    """
    task = get_task(db, task_id)
    if not task or task.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    try:
        updated_task = update_task_status(
            db, task_id, current_user.id, TaskStatus.COMPLETED
        )
        
        # Notify admin about task completion
        task_creator = get_task_creator(db, task_id)
        if task_creator:
            await notify_task_completion(db, updated_task, current_user, task_creator)
        
        return {"message": "Task marked as completed"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


# ==================== Notification Preferences ====================

@app.put("/user/notifications/preferences")
async def update_notification_preference(
    receive_notifications: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update email notification preferences
    """
    success = update_user_notifications(db, current_user.id, receive_notifications)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update notification preferences"
        )
    
    status_msg = "enabled" if receive_notifications else "disabled"
    return {"message": f"Email notifications {status_msg}"}


@app.post("/user/notifications/unsubscribe")
async def unsubscribe_emails(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe from email notifications (uses email, no auth required)
    """
    from assignment2_models import User as UserModel
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        # Return success anyway for security (don't reveal if email exists)
        return {"message": "If the email exists, you have been unsubscribed"}
    
    user.receive_notifications = False
    db.commit()
    return {"message": "Successfully unsubscribed from email notifications"}


# ==================== Health Check ====================

@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "message": "Welcome to Advanced Todo List API",
        "version": APP_VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
