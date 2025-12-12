from fastapi import FastAPI, status, HTTPException
from models import Task, TaskCreate, TaskUpdate
from typing import List

# Path - It is used to validate and document path variables (input in the URL)
from fastapi import Path

# Query - It is used for query parameters in FastAPI
from fastapi import Query

app = FastAPI()


@app.get("/")
async def greet():
    return {"message": "Welcome"}


my_tasks = [
    Task(id=1, name="task1", status="completed"),
    Task(id=2, name="task2", status="pending"),
    Task(id=3, name="task3", status="pending"),
    Task(id=4, name="task4", status="completed"),
    Task(id=5, name="task5", status="pending"),
]


# Get request to fetch the data
# TODO: Add query parameters for searching tasks by name -> `starts_with`
# TODO: Add sort query param -> `sort_by=(asc(default)|desc)`
@app.get("/tasks", response_model=List[Task])
def get_tasks(limit: int = Query(2)):
    return my_tasks[:limit]


# Get tasks by id
@app.get("/task/{id}", response_model=Task)
async def get_task_by_id(id: int = Path(gt=0)):
    for task in my_tasks:
        if task.id == id:
            return task
    raise HTTPException(status_code=404, detail="Task not found!")


# Add/Create new task using POST request
@app.post("/add_task", response_model=Task, status_code=status.HTTP_201_CREATED)
async def add_new_task(task: TaskCreate):
    my_tasks.append(task)
    return task


# Edit data using PUT request
@app.put("/edit_task/{id}", response_model=Task)
async def edit_task(id: int, updated_task: TaskUpdate):
    for i in range(len(my_tasks)):
        if my_tasks[i].id == id:
            my_tasks[i].name = updated_task.name
            my_tasks[i].status = updated_task.status
            return my_tasks[i]

    raise HTTPException(status_code=404, detail="Task not found!")


# Delete task using Delete request
@app.delete("/task_delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    for i in range(len(my_tasks)):
        if my_tasks[i].id == id:
            del my_tasks[i]
            return "Product deleted"
    raise HTTPException(status_code=404, detail="Task not found!")
