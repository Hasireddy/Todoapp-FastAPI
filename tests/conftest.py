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
from database_models import Base, UserDB, TaskDB
from auth import hash_password



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

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database."""
    user = UserDB(
        username="testuser",
        hashed_password=hash_password("testpass123"),
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user."""
    admin = UserDB(
        username="testadmin",
        hashed_password=hash_password("adminpass123"),
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for a regular user."""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """Get authentication headers for an admin user."""
    response = client.post(
        "/token",
        data={"username": "testadmin", "password": "adminpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_task(db_session, test_user):
    """Create a sample task for testing."""
    task = TaskDB(
        name="Test Task",
        status="pending",
        user_id=test_user.id
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task
