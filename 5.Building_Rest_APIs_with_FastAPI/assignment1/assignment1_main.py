import os
print(" RUNNING FILE:", __file__)
print(" CWD:", os.getcwd())



from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

from assignment1_config import APP_NAME, APP_VERSION, ACCESS_TOKEN_EXPIRE_MINUTES
from assignment1_database import engine, Base, get_db
from assignment1_models import User
from assignment1_schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    TaskCreate, TaskResponse, TaskUpdate
)
from assignment1_auth import (
    create_access_token, get_current_user
)
from assignment1_crud import (
    create_user, authenticate_user, get_all_tasks, create_task,
    get_task, update_task, delete_task
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="A To-Do List API with user authentication --by Omkar "
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tasks", response_model=TaskResponse)
async def create_new_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_task(db, task, current_user.id)


@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_tasks(db, current_user.id)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Todo List API",
        "version": APP_VERSION,
        "docs": "/docs"
    }

@app.get("/whoami")
def whoami():
    return {"assignment": "ASSIGNMENT 1"}
