from pydantic import BaseModel

class Tasks(BaseModel):
    id:int
    name:str
    status:str