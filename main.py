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


#Add/Create new task using POST request

@app.post("/add_task")

async def add_new_task(task:Tasks):
    my_tasks.append(task)
    return "New task added"


# Edit data using PUT request

@app.put("/edit_task/{id}")

async def edit_task(id:int,updated_task:Tasks):
    for i in range(len(my_tasks)):
        if my_tasks[i].id == id:
            my_tasks[i] = updated_task
            return "Task updated successfully"
    return "No task found"
        
            
# Delete task using Delete request

@app.delete("/task_delete/{id}")

async def delete_task(id:int):
    for i in range(len(my_tasks)):
        if my_tasks[i].id == id:
            del my_tasks[i]
            return "Product deleted"
    return "No product found"

