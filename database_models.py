from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()


class UserDB(Base):
    """Database model for users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship: One user can have many tasks
    tasks = relationship("TaskDB", back_populates="owner")


class TaskDB(Base):
    """Database model for tasks."""

    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign key: Each task belongs to a user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship: Task belongs to one owner
    owner = relationship("UserDB", back_populates="tasks")
