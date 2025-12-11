from fastapi import FastAPI
from models import Tasks

app = FastAPI()

@app.get("/")
async def greet():
    return {"message":"Welcome"}

my_tasks = [
    Tasks(id=1,name="task1",status="completed"),
    Tasks(id=2,name="task2",status="pending"),
    Tasks(id=3,name="task3",status="pending"),
    Tasks(id=4,name="task4",status="completed"),
    Tasks(id=5,name="task5",status="pending"),
   
]


#Get request to fetch the data

@app.get("/tasks")

def get_tasks():
    return my_tasks


#Get tasks by id

@app.get("/task/{id}")

async def get_task_by_id(id:int):
    for task in my_tasks:
        if task.id == id:
            return task
    return "Task not found"
