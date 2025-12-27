from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== USER MODELS ====================


class UserBase(BaseModel):
    """Base user model with common fields."""

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_]+$",
        description="Username (alphanumeric and underscores only)",
    )


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(
        min_length=6, max_length=100, description="Password (minimum 6 characters)"
    )
    role: str = Field(
        default="user",
        pattern="^(user|admin)$",
        description="User role: 'user' or 'admin'",
    )


class User(UserBase):
    """User response model (excludes password)."""

    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== TASK MODELS ====================


class TaskBase(BaseModel):
    """Base task model with common fields."""

    name: Optional[str] = Field(
        min_length=5,
        max_length=50,
        pattern="^[A-Za-z].*$",
        description="Task name (must start with a letter)",
    )
    status: str = Field(
        default="pending",
        pattern="^(pending|in progress|completed)$",
        description="Task status",
    )


class TaskCreate(TaskBase):
    """Model for creating a new task (no ID needed, auto-generated)."""

    pass


class TaskUpdate(BaseModel):
    """Model for updating a task (all fields optional)."""

    name: Optional[str] = Field(
        None,
        min_length=5,
        max_length=50,
        pattern="^[A-Za-z].*$",
        description="Task name (must start with a letter)",
    )
    status: Optional[str] = Field(
        None, pattern="^(pending|in progress|completed)$", description="Task status"
    )


class Task(TaskBase):
    """Task response model with all fields."""

    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskWithOwner(Task):
    """Task response model including owner information."""

    owner_username: Optional[str] = None
