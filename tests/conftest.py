# Fixtures: Functions that will run before your tests to set up required state for your tests to run.
# Example - Database Connection; Test Data
import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator

from main import app
from database import get_db
from database_models import Base



# SQLite -> In-memory DB creation
db_url = "sqlite:///:memory:"

engine = create_engine(
    db_url, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db() -> Generator:
    """
    Dependency that provides a database session.

    Yields a database session and ensures it's properly closed
    after the request is complete.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# FASTApi Server -> DB Object -> App Instance
# Testing -> DB Object -> Testing Client 

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    # Client Requires a DB Session To Work With: db_session -> client
    app.dependency_overrides[get_db] = override_get_db

    # FastAPI Server: Provides a TestClient class that simulates HTTP requests by running a real server
    client = TestClient(app)
    yield client


# Create a fixture -> test_user
# It will create a test user and save it in your DB so that we can use it for login workflows
# Depends on db_session fixture





