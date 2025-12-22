from fastapi import FastAPI, status, HTTPException, Depends, Response, Path, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import List, Optional

from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    create_user,
    get_user_by_username,
)
from models import Task, TaskCreate, TaskUpdate, User, UserCreate
from database import engine, get_db, SessionLocal
from database_models import TaskDB, UserDB, Base

app = FastAPI(
    title="Todo App API",
    description="A secure Todo application with JWT authentication and user-task relationships",
)


# Create all tables in the database
Base.metadata.create_all(bind=engine)


def init_db():
    """Initialize the database with default admin user if empty."""
    with SessionLocal() as db:
        # Create default admin user if no users exist
        user_count = db.query(UserDB).count()
        if user_count == 0:
            admin = create_user(db, username="admin", password="admin123", role="admin")
            demo_user = create_user(
                db, username="demo", password="demo123", role="user"
            )

            # Create some sample tasks for the demo user
            sample_tasks = [
                TaskDB(name="Planning", status="completed", user_id=demo_user.id),
                TaskDB(name="Coding", status="pending", user_id=demo_user.id),
                TaskDB(name="Research", status="pending", user_id=admin.id),
                TaskDB(name="Meeting", status="completed", user_id=admin.id),
            ]
            for task in sample_tasks:
                db.add(task)
            db.commit()


init_db()


# ==================== PUBLIC ENDPOINTS ====================


@app.get("/")
async def greet():
    """Welcome endpoint - public access."""
    return {"message": "Welcome to the Todo App API"}


# ==================== AUTHENTICATION ENDPOINTS ====================


@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.
    Use the returned token in the Authorization header as: Bearer <token>
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        {"sub": user.username, "role": user.role, "user_id": user.id}
    )

    return {"access_token": token, "token_type": "bearer"}


@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    """
    # Check if username already exists
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = create_user(
        db,
        username=user_data.username,
        password=user_data.password,
        role=user_data.role,
    )
    return user


@app.get("/me", response_model=User)
def get_current_user_info(current_user: UserDB = Depends(get_current_user)):
    """Get information about the currently authenticated user."""
    return current_user


# ==================== TASK ENDPOINTS ====================


@app.get("/tasks", response_model=List[Task])
async def get_all_tasks(
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of tasks to return"
    ),
    offset: int = Query(
        default=0, ge=0, description="Number of tasks to skip (for pagination)"
    ),
    starts_with: Optional[str] = Query(
        default=None,
        max_length=50,
        description="Filter tasks whose name starts with this string",
    ),
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        pattern="^(pending|in progress|completed)$",
        description="Filter by status",
    ),
    sort_by: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort by name: 'asc' or 'desc'",
    ),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Retrieve tasks from the database with filtering, sorting, and pagination.

    - **limit**: Maximum number of tasks to return (default: 100, max: 1000)
    - **offset**: Number of tasks to skip for pagination (default: 0)
    - **starts_with**: Filter tasks whose name starts with this string
    - **status**: Filter by task status (pending, in progress, completed)
    - **sort_by**: Sort by name ascending ('asc') or descending ('desc')

    Admin users see all tasks, regular users see only their own.
    """
    # Base query based on user role
    if current_user.role == "admin":
        query = db.query(TaskDB)
    else:
        query = db.query(TaskDB).filter(TaskDB.user_id == current_user.id)

    # Apply filters
    if starts_with:
        query = query.filter(TaskDB.name.startswith(starts_with))

    if status_filter:
        query = query.filter(TaskDB.status == status_filter)

    # Apply sorting
    if sort_by == "desc":
        query = query.order_by(desc(TaskDB.name))
    else:
        query = query.order_by(asc(TaskDB.name))

    # Apply pagination
    query = query.offset(offset).limit(limit)

    db_tasks = query.all()

    if starts_with and not db_tasks:
        raise HTTPException(
            status_code=404, detail=f"No tasks found starting with '{starts_with}'"
        )

    return db_tasks


@app.get("/my-tasks", response_model=List[Task])
async def get_my_tasks(
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of tasks to return"
    ),
    offset: int = Query(
        default=0, ge=0, description="Number of tasks to skip (for pagination)"
    ),
    starts_with: Optional[str] = Query(
        default=None,
        max_length=50,
        description="Filter tasks whose name starts with this string",
    ),
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        pattern="^(pending|in progress|completed)$",
        description="Filter by status",
    ),
    sort_by: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort by name: 'asc' or 'desc'",
    ),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Retrieve only the current user's tasks with filtering, sorting, and pagination.

    - **limit**: Maximum number of tasks to return (default: 100)
    - **offset**: Number of tasks to skip for pagination
    - **starts_with**: Filter tasks whose name starts with this string
    - **status**: Filter by task status
    - **sort_by**: Sort by name ascending or descending
    """
    query = db.query(TaskDB).filter(TaskDB.user_id == current_user.id)

    # Apply filters
    if starts_with:
        query = query.filter(TaskDB.name.startswith(starts_with))

    if status_filter:
        query = query.filter(TaskDB.status == status_filter)

    # Apply sorting
    if sort_by == "desc":
        query = query.order_by(desc(TaskDB.name))
    else:
        query = query.order_by(asc(TaskDB.name))

    # Apply pagination
    query = query.offset(offset).limit(limit)

    return query.all()


@app.get("/task/{id}", response_model=Task)
async def get_task_by_id(
    id: int = Path(gt=0, description="Task ID must be greater than 0"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Retrieve a specific task by ID.
    Users can only view their own tasks unless they are admin.
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check ownership (admin can see all)
    if current_user.role != "admin" and db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")

    return db_task


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Create a new task.
    Task is automatically associated with the current user.
    """
    db_task = TaskDB(
        name=task.name,
        status=task.status,
        user_id=current_user.id,  # Automatically associate with current user
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.put("/task/{id}", response_model=Task)
async def update_task(
    updated_task: TaskUpdate,
    id: int = Path(gt=0, description="Task ID must be greater than 0"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Update an existing task.
    Users can only update their own tasks unless they are admin.
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check ownership (admin can update all)
    if current_user.role != "admin" and db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this task"
        )

    # Only update fields that are provided
    if updated_task.name is not None:
        db_task.name = updated_task.name
    if updated_task.status is not None:
        db_task.status = updated_task.status

    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/task/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: int = Path(gt=0, description="Task ID must be greater than 0"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Delete a task by ID.
    Users can only delete their own tasks unless they are admin.
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check ownership (admin can delete all)
    if current_user.role != "admin" and db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this task"
        )

    db.delete(db_task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==================== USER MANAGEMENT (ADMIN ONLY) ====================


@app.get("/users", response_model=List[User])
async def get_all_users(
    db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)
):
    """Get all users (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return db.query(UserDB).all()


@app.get("/user/{user_id}/tasks", response_model=List[Task])
async def get_user_tasks(
    user_id: int = Path(gt=0, description="User ID"),
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of tasks to return"
    ),
    offset: int = Query(default=0, ge=0, description="Number of tasks to skip"),
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        pattern="^(pending|in progress|completed)$",
        description="Filter by status",
    ),
    sort_by: str = Query(
        default="asc", pattern="^(asc|desc)$", description="Sort by name"
    ),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Get all tasks for a specific user (admin only, or own tasks)."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these tasks"
        )

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(TaskDB).filter(TaskDB.user_id == user_id)

    if status_filter:
        query = query.filter(TaskDB.status == status_filter)

    if sort_by == "desc":
        query = query.order_by(desc(TaskDB.name))
    else:
        query = query.order_by(asc(TaskDB.name))

    return query.offset(offset).limit(limit).all()
