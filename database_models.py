from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String

Base = declarative_base()

class Task(Base):
    __tablename__ = "task"
    id = Column(Integer,primary_key=True,Index=True)
    name = Column(String)
    status = Column(String)
