from fastapi import FastAPI
from models import Tasks

app = FastAPI()

@app.get("/")
async def greet():
    return {"message":"Welcome"}

my_list = [
    Tasks(id=1,name="task1",status="completed"),
    Tasks(id=2,name="task2",status="pending"),
    Tasks(id=3,name="task3",status="pending"),
    Tasks(id=4,name="task4",status="completed"),
    Tasks(id=5,name="task5",status="pending"),
   
]
