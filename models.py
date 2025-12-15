from typing import Optional
from pydantic import BaseModel, Field


class Task(BaseModel):
    id: int
    # TODO: Add a rule that description cannot contain numbers and should be only alphabets.
    name: Optional[str] = Field(
        min_length=5,
        max_length=20,
        description="Description of the task to be performed.",
    )
    status: str = Field(pattern="^(pending|in progress|completed)$")


# TaskCreate -> Client Side Task Object -> Server Saves It - > Task
class TaskCreate(Task):
    pass


# UpdatedTask -> Copy of Original Task (Client have modified some data)
class TaskUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=5,
        max_length=20,
        description="Description of the task to be performed.",
    )
    status: str = Field(pattern="^(pending|in progress|completed)$")