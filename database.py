from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Engine: Connect to DB
# Session: Open connection where we interact with DB
# Base: Base class models for creating SQLAlchemy ORM
# Model: Python Class -> DB Table

#db_url = "sqlite:///./tasks.db"
db_url = "postgresql://postgres:root@localhost:5432/tasks"
engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

get_db()
