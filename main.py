from fastapi import FastAPI, status, HTTPException, Depends
from typing import List, Optional
from models import Task, TaskCreate, TaskUpdate
from database import engine, get_db,SessionLocal
from database_models import TaskDB
from sqlalchemy.orm import Session

# Path - It is used to validate and document path variables (input in the URL)
from fastapi import Path

# Query - It is used for query parameters in FastAPI
from fastapi import Query

app = FastAPI()

@app.get("/")
async def greet():
    return {"message": "Welcome"}


my_tasks = [
    Task(id=1, name="Planning", status="completed"),
    Task(id=2, name="Coding", status="pending"),
    Task(id=3, name="Research", status="pending"),
    Task(id=4, name="Meeting", status="completed"),
    Task(id=5, name="Testing", status="pending"),
    Task(id=6, name="Documentation", status="pending"),
]



# Create tables in the database from the database models
TaskDB.metadata.create_all(bind=engine)


#Inserting data into the Dtabase

def init_db():
    with SessionLocal() as db:
        count = db.query(TaskDB).count()
        if count == 0:
            for task in my_tasks:
                db.add(TaskDB(**task.model_dump()))
            db.commit()


       

init_db()
    

# Get request to fetch the data
# Add query parameters for searching tasks by name -> `starts_with`
# Add sort query param -> `sort_by=(asc(default)|desc)`
@app.get("/tasks", response_model=List[Task])
async def get_tasks(
    db: Session = Depends(get_db),
    limit: int = Query(4, description="Maximum number of tasks to return"),
    starts_with: Optional[str] = Query(
        None, description="Filter tasks whose name starts with this string"
    ),
    sort_by: str = Query("asc", description="Sort tasks by name:'asc' or 'desc' "),
):
    my_tasks = db.query(TaskDB).all()
    if limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")
    if starts_with:
        filtered_tasks = [
            task for task in my_tasks if task.name.startswith(starts_with)
        ]
        if not filtered_tasks:
            raise HTTPException(
                status_code=404, detail=f"No tasks found starting with '{starts_with}'"
            )
    # If starts with query parameter is not provided return all tasks
    else:
        filtered_tasks = my_tasks

    # Validate sort_by
    if sort_by not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'asc' or 'desc'")
    # Sort tasks by name
    filtered_tasks.sort(key=lambda t: t.name, reverse=(sort_by == "desc"))

    return filtered_tasks[:limit]


# Get tasks by id
# TODO: Use DB object
@app.get("/task/{id}", response_model=Task)
async def get_task_by_id(id: int = Path(gt=0)):
    for task in my_tasks:
        if task.id == id:
            return task
    raise HTTPException(status_code=404, detail="Task not found!")


# Add/Create new task using POST request
@app.post("/add_task", response_model=Task, status_code=status.HTTP_201_CREATED)
async def add_new_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskDB(id=task.id, name=task.name, status=task.status)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# Edit data using PUT request
# TODO: Use DB object
@app.put("/edit_task/{id}", response_model=Task)
async def edit_task(id: int, updated_task: TaskUpdate):
    for i in range(len(my_tasks)):
        if my_tasks[i].id == id:
            my_tasks[i].name = updated_task.name
            my_tasks[i].status = updated_task.status
            return my_tasks[i]

    raise HTTPException(status_code=404, detail="Task not found!")


# Delete task using Delete request
# TODO: Use DB object
@app.delete("/task_delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    for i in range(len(my_tasks)):
        if my_tasks[i].id == id:
            del my_tasks[i]
            return "Product deleted"
    raise HTTPException(status_code=404, detail="Task not found!")
