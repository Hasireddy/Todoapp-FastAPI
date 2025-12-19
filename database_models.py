from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String

Base = declarative_base()

class TaskDB(Base):
    __tablename__ = "task"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    status = Column(String)
