# 🧪 Complete Guide to Testing FastAPI with Pytest

A beginner-friendly, comprehensive guide to adding unit tests to your Todo App using pytest.

---

## 📋 Table of Contents

1. [What is Pytest?](#-what-is-pytest)
2. [Why Write Tests?](#-why-write-tests)
3. [Installation & Setup](#-installation--setup)
4. [Pytest Basics](#-pytest-basics)
5. [Testing FastAPI Applications](#-testing-fastapi-applications)
6. [Project Test Structure](#-project-test-structure)
7. [Writing Your First Test](#-writing-your-first-test)
8. [Fixtures - Reusable Test Setup](#-fixtures---reusable-test-setup)
9. [Testing Authentication](#-testing-authentication)
10. [Testing CRUD Operations](#-testing-crud-operations)
11. [Testing Edge Cases & Errors](#-testing-edge-cases--errors)
12. [Running Tests](#-running-tests)
13. [Test Coverage](#-test-coverage)
14. [Best Practices](#-best-practices)
15. [Complete Test File](#-complete-test-file)

---

## 🤔 What is Pytest?

**Pytest** is Python's most popular testing framework. It makes writing and running tests simple and enjoyable.

### Key Features

| Feature | Description |
|---------|-------------|
| **Simple Syntax** | Just use `assert` statements - no complex APIs |
| **Auto-Discovery** | Automatically finds tests in files starting with `test_` |
| **Fixtures** | Reusable setup/teardown code |
| **Plugins** | Rich ecosystem (coverage, async, mocking) |
| **Detailed Output** | Clear failure messages showing exactly what went wrong |

### Pytest vs Unittest (Python's Built-in)

```python
# unittest (verbose, class-based)
import unittest

class TestMath(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)

if __name__ == '__main__':
    unittest.main()


# pytest (simple, function-based)
def test_addition():
    assert 1 + 1 == 2

# That's it! Just run: pytest
```

---

## 💡 Why Write Tests?

### Without Tests 😰
```
1. Write code
2. Manually test in browser/Postman
3. Push to production
4. 🔥 Bug appears
5. "It worked on my machine!"
6. Spend hours debugging
7. Repeat...
```

### With Tests 😎
```
1. Write test first (optional: TDD)
2. Write code
3. Run tests automatically
4. ✅ All pass → Safe to deploy
5. ❌ Test fails → Bug caught before production
6. Refactor confidently
```

### What Tests Catch

- ✅ Broken authentication
- ✅ Database query errors
- ✅ Validation bypasses
- ✅ Authorization failures
- ✅ Edge cases (empty inputs, nulls)
- ✅ Regressions (new code breaking old features)

---

## 📦 Installation & Setup

### Step 1: Install Dependencies

```bash
# Core testing packages
pip install pytest pytest-asyncio httpx

# Optional: Coverage reporting
pip install pytest-cov
```

| Package | Purpose |
|---------|---------|
| `pytest` | The testing framework |
| `pytest-asyncio` | Test async functions (FastAPI uses async) |
| `httpx` | HTTP client for testing FastAPI (like requests, but async) |
| `pytest-cov` | Code coverage reporting |

### Step 2: Create pytest Configuration

Create `pytest.ini` in your project root:

```ini
# pytest.ini
[pytest]
# Minimum pytest version
minversion = 7.0

# Directories to search for tests
testpaths = tests

# File patterns to consider as tests
python_files = test_*.py

# Function patterns to consider as tests
python_functions = test_*

# Enable async testing
asyncio_mode = auto

# Show extra test summary info
addopts = -v --tb=short

# Ignore these directories
norecursedirs = venv .git __pycache__
```

### Step 3: Alternative - pyproject.toml Configuration

If you prefer `pyproject.toml`:

```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = "-v --tb=short"
```

---

## 📚 Pytest Basics

### Basic Test Structure

```python
# test_example.py

def test_something():
    """Test description (shown in output)."""
    # Arrange - Set up test data
    x = 5
    y = 3
    
    # Act - Perform the action
    result = x + y
    
    # Assert - Check the result
    assert result == 8
```

### The `assert` Statement

Pytest uses plain Python `assert`. If the assertion fails, pytest shows helpful output:

```python
def test_string_comparison():
    expected = "hello world"
    actual = "hello Word"  # Note: capital W
    assert actual == expected

# Output on failure:
# AssertionError: assert 'hello Word' == 'hello world'
#   - hello Word
#   + hello world
```

### Common Assertions

```python
# Equality
assert result == expected
assert result != unexpected

# Boolean
assert is_valid is True
assert error is None

# Collections
assert item in my_list
assert len(my_list) == 5
assert "key" in my_dict

# Exceptions (more on this later)
with pytest.raises(ValueError):
    int("not a number")

# Approximate equality (for floats)
assert result == pytest.approx(3.14159, rel=0.01)
```

### Test Naming Convention

```python
# ✅ Good - descriptive names
def test_login_with_valid_credentials_returns_token():
    ...

def test_create_task_without_auth_returns_401():
    ...

def test_delete_nonexistent_task_returns_404():
    ...

# ❌ Bad - vague names
def test_login():
    ...

def test_1():
    ...
```

---

## 🚀 Testing FastAPI Applications

### How FastAPI Testing Works

FastAPI provides a `TestClient` that simulates HTTP requests without running a real server:

```python
from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

# Make requests just like a real HTTP client
response = client.get("/")
assert response.status_code == 200
assert response.json() == {"message": "Welcome to the Todo App API"}
```

### Sync vs Async Testing

FastAPI endpoints are async, but `TestClient` handles this for you:

```python
# Your async endpoint
@app.get("/tasks")
async def get_tasks():  # async function
    return []

# Your test (no async needed!)
def test_get_tasks():  # regular function
    response = client.get("/tasks")
    assert response.status_code == 200
```

For truly async tests (testing async functions directly):

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

---

## 📁 Project Test Structure

### Recommended Structure

```
todo-app/
├── main.py
├── auth.py
├── database.py
├── database_models.py
├── models.py
├── pytest.ini              # ← Pytest configuration
├── conftest.py             # ← Shared fixtures (optional, can be in tests/)
└── tests/                  # ← All tests in this folder
    ├── __init__.py         # ← Makes it a Python package
    ├── conftest.py         # ← Shared fixtures for tests
    ├── test_auth.py        # ← Authentication tests
    ├── test_tasks.py       # ← Task CRUD tests
    └── test_users.py       # ← User tests
```

### What Goes Where

| File | Purpose |
|------|---------|
| `pytest.ini` | Pytest configuration |
| `conftest.py` | Shared fixtures (test setup, database, clients) |
| `test_auth.py` | Login, register, token tests |
| `test_tasks.py` | Create, read, update, delete task tests |
| `test_users.py` | User management tests |

---

## ✏️ Writing Your First Test

### Step 1: Create Test Directory

```bash
mkdir tests
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_basic.py
```

### Step 2: Write a Simple Test

```python
# tests/test_basic.py
"""Basic tests to verify the API is working."""

from fastapi.testclient import TestClient
import sys
sys.path.insert(0, '..')  # Add parent directory to path

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test that the root endpoint returns welcome message."""
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Todo App API"}


def test_root_endpoint_method_not_allowed():
    """Test that POST to root returns 405."""
    response = client.post("/")
    assert response.status_code == 405
```

### Step 3: Run Your First Test

```bash
# From project root
pytest tests/test_basic.py -v

# Output:
# tests/test_basic.py::test_root_endpoint PASSED
# tests/test_basic.py::test_root_endpoint_method_not_allowed PASSED
```

---

## 🔧 Fixtures - Reusable Test Setup

### What are Fixtures?

Fixtures are functions that run before tests to set up required state (database connections, test data, authenticated clients, etc.).

### Basic Fixture Example

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


# test_basic.py
def test_root(client):  # 'client' fixture is injected automatically
    response = client.get("/")
    assert response.status_code == 200
```

### Fixture for Test Database

We need a separate test database so tests don't affect real data:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import from your app
import sys
sys.path.insert(0, '..')
from main import app
from database import get_db
from database_models import Base, UserDB, TaskDB
from auth import hash_password


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Required for in-memory SQLite
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the database dependency with test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    yield db
    
    # Cleanup after test
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database."""
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create tables for this test
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


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
```

### Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default: runs for each test
@pytest.fixture(scope="class")     # Runs once per test class
@pytest.fixture(scope="module")    # Runs once per test file
@pytest.fixture(scope="session")   # Runs once per test session
```

---

## 🔐 Testing Authentication

```python
# tests/test_auth.py
"""Tests for authentication endpoints."""

import pytest


class TestRegistration:
    """Tests for user registration."""
    
    def test_register_new_user(self, client):
        """Test successful user registration."""
        response = client.post(
            "/register",
            json={
                "username": "newuser",
                "password": "password123",
                "role": "user"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "user"
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username fails."""
        response = client.post(
            "/register",
            json={
                "username": "testuser",  # Already exists (from test_user fixture)
                "password": "password123",
                "role": "user"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_invalid_username(self, client):
        """Test registration with invalid username fails."""
        response = client.post(
            "/register",
            json={
                "username": "ab",  # Too short (min 3)
                "password": "password123",
                "role": "user"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_weak_password(self, client):
        """Test registration with short password fails."""
        response = client.post(
            "/register",
            json={
                "username": "validuser",
                "password": "123",  # Too short (min 6)
                "role": "user"
            }
        )
        
        assert response.status_code == 422


class TestLogin:
    """Tests for login endpoint."""
    
    def test_login_success(self, client, test_user):
        """Test successful login returns token."""
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails."""
        response = client.post(
            "/token",
            data={
                "username": "doesnotexist",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Tests for authentication requirement on protected endpoints."""
    
    def test_access_without_token(self, client):
        """Test that protected endpoints require authentication."""
        response = client.get("/tasks")
        assert response.status_code == 401
    
    def test_access_with_invalid_token(self, client):
        """Test that invalid tokens are rejected."""
        response = client.get(
            "/tasks",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401
    
    def test_access_with_valid_token(self, client, auth_headers):
        """Test that valid tokens allow access."""
        response = client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200


class TestCurrentUser:
    """Tests for /me endpoint."""
    
    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user info."""
        response = client.get("/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["role"] == "user"
```

---

## 📝 Testing CRUD Operations

```python
# tests/test_tasks.py
"""Tests for task CRUD operations."""

import pytest


class TestCreateTask:
    """Tests for creating tasks."""
    
    def test_create_task_success(self, client, auth_headers):
        """Test creating a task with valid data."""
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={
                "name": "New Task",
                "status": "pending"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Task"
        assert data["status"] == "pending"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
    
    def test_create_task_without_auth(self, client):
        """Test creating task without authentication fails."""
        response = client.post(
            "/tasks",
            json={"name": "Test Task", "status": "pending"}
        )
        
        assert response.status_code == 401
    
    def test_create_task_invalid_name(self, client, auth_headers):
        """Test creating task with invalid name fails."""
        # Name too short (min 5 characters)
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"name": "Test", "status": "pending"}
        )
        
        assert response.status_code == 422
    
    def test_create_task_invalid_status(self, client, auth_headers):
        """Test creating task with invalid status fails."""
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"name": "Valid Name", "status": "invalid_status"}
        )
        
        assert response.status_code == 422


class TestReadTasks:
    """Tests for reading tasks."""
    
    def test_get_all_tasks(self, client, auth_headers, sample_task):
        """Test getting all tasks for a user."""
        response = client.get("/tasks", headers=auth_headers)
        
        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)
        assert len(tasks) >= 1
    
    def test_get_my_tasks(self, client, auth_headers, sample_task):
        """Test getting only current user's tasks."""
        response = client.get("/my-tasks", headers=auth_headers)
        
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        # All tasks should belong to current user
        for task in tasks:
            assert task["user_id"] == sample_task.user_id
    
    def test_get_task_by_id(self, client, auth_headers, sample_task):
        """Test getting a specific task by ID."""
        response = client.get(
            f"/task/{sample_task.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["name"] == sample_task.name
    
    def test_get_nonexistent_task(self, client, auth_headers):
        """Test getting a task that doesn't exist."""
        response = client.get("/task/99999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestQueryParameters:
    """Tests for query parameters on task listing."""
    
    def test_filter_by_status(self, client, auth_headers, db_session, test_user):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        from database_models import TaskDB
        
        for status in ["pending", "completed", "pending"]:
            task = TaskDB(name=f"Task {status}", status=status, user_id=test_user.id)
            db_session.add(task)
        db_session.commit()
        
        # Filter by pending
        response = client.get(
            "/tasks?status=pending",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        tasks = response.json()
        for task in tasks:
            assert task["status"] == "pending"
    
    def test_limit_results(self, client, auth_headers, db_session, test_user):
        """Test limiting number of results."""
        # Create multiple tasks
        from database_models import TaskDB
        
        for i in range(5):
            task = TaskDB(name=f"Task Number{i}", status="pending", user_id=test_user.id)
            db_session.add(task)
        db_session.commit()
        
        response = client.get("/tasks?limit=2", headers=auth_headers)
        
        assert response.status_code == 200
        assert len(response.json()) <= 2
    
    def test_sort_descending(self, client, auth_headers, sample_task):
        """Test sorting tasks descending."""
        response = client.get(
            "/tasks?sort_by=desc",
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestUpdateTask:
    """Tests for updating tasks."""
    
    def test_update_task_success(self, client, auth_headers, sample_task):
        """Test updating a task."""
        response = client.put(
            f"/task/{sample_task.id}",
            headers=auth_headers,
            json={"status": "completed"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
    
    def test_update_nonexistent_task(self, client, auth_headers):
        """Test updating a non-existent task."""
        response = client.put(
            "/task/99999",
            headers=auth_headers,
            json={"status": "completed"}
        )
        
        assert response.status_code == 404
    
    def test_update_other_users_task(self, client, admin_headers, sample_task, db_session):
        """Test that admin can update any task."""
        response = client.put(
            f"/task/{sample_task.id}",
            headers=admin_headers,
            json={"status": "completed"}
        )
        
        # Admin should be able to update any task
        assert response.status_code == 200


class TestDeleteTask:
    """Tests for deleting tasks."""
    
    def test_delete_task_success(self, client, auth_headers, sample_task):
        """Test deleting a task."""
        response = client.delete(
            f"/task/{sample_task.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify task is deleted
        get_response = client.get(
            f"/task/{sample_task.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_task(self, client, auth_headers):
        """Test deleting a non-existent task."""
        response = client.delete("/task/99999", headers=auth_headers)
        
        assert response.status_code == 404
```

---

## ⚠️ Testing Edge Cases & Errors

```python
# tests/test_edge_cases.py
"""Tests for edge cases and error handling."""

import pytest


class TestInputValidation:
    """Tests for input validation."""
    
    def test_task_name_with_special_chars(self, client, auth_headers):
        """Test task name must start with a letter."""
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"name": "123Invalid", "status": "pending"}
        )
        
        assert response.status_code == 422
    
    def test_empty_request_body(self, client, auth_headers):
        """Test creating task with empty body."""
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 422
    
    def test_invalid_json(self, client, auth_headers):
        """Test sending invalid JSON."""
        response = client.post(
            "/tasks",
            headers=auth_headers,
            content="not valid json",
            headers={"Content-Type": "application/json", **auth_headers}
        )
        
        assert response.status_code == 422


class TestAuthorization:
    """Tests for authorization (not just authentication)."""
    
    def test_user_cannot_see_others_task(self, client, db_session, test_user):
        """Test that users cannot access other users' tasks."""
        from database_models import UserDB, TaskDB
        from auth import hash_password
        
        # Create another user with a task
        other_user = UserDB(
            username="otheruser",
            hashed_password=hash_password("password123"),
            role="user"
        )
        db_session.add(other_user)
        db_session.commit()
        
        other_task = TaskDB(
            name="Other Task",
            status="pending",
            user_id=other_user.id
        )
        db_session.add(other_task)
        db_session.commit()
        
        # Login as test_user
        login_response = client.post(
            "/token",
            data={"username": "testuser", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access other user's task
        response = client.get(f"/task/{other_task.id}", headers=headers)
        
        assert response.status_code == 403
    
    def test_admin_can_see_all_tasks(self, client, admin_headers, sample_task):
        """Test that admin can access any task."""
        response = client.get(f"/task/{sample_task.id}", headers=admin_headers)
        
        assert response.status_code == 200
    
    def test_non_admin_cannot_list_users(self, client, auth_headers):
        """Test that regular users cannot list all users."""
        response = client.get("/users", headers=auth_headers)
        
        assert response.status_code == 403


class TestPagination:
    """Tests for pagination edge cases."""
    
    def test_offset_beyond_results(self, client, auth_headers):
        """Test offset larger than total results."""
        response = client.get("/tasks?offset=10000", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_negative_limit_rejected(self, client, auth_headers):
        """Test that negative limit is rejected."""
        response = client.get("/tasks?limit=-1", headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_limit_exceeds_maximum(self, client, auth_headers):
        """Test that limit above maximum is rejected."""
        response = client.get("/tasks?limit=10000", headers=auth_headers)
        
        assert response.status_code == 422
```

---

## ▶️ Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test class
pytest tests/test_auth.py::TestLogin

# Run specific test function
pytest tests/test_auth.py::TestLogin::test_login_success

# Run tests matching a pattern
pytest -k "login"  # Runs all tests with "login" in name

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run last failed tests
pytest --lf
```

### Understanding Output

```
$ pytest -v

tests/test_auth.py::TestLogin::test_login_success PASSED     [ 20%]
tests/test_auth.py::TestLogin::test_login_wrong_password PASSED [ 40%]
tests/test_tasks.py::TestCreateTask::test_create_task_success PASSED [ 60%]
tests/test_tasks.py::TestCreateTask::test_create_task_invalid FAILED [ 80%]
tests/test_tasks.py::TestReadTasks::test_get_all_tasks PASSED [100%]

======================== FAILURES ========================
___ TestCreateTask.test_create_task_invalid ___

    def test_create_task_invalid(self, client, auth_headers):
>       assert response.status_code == 422
E       AssertionError: assert 400 == 422

tests/test_tasks.py:45: AssertionError
================ 1 failed, 4 passed in 0.52s ================
```

### Test Output Symbols

| Symbol | Meaning |
|--------|---------|
| `.` or `PASSED` | Test passed |
| `F` or `FAILED` | Test failed |
| `E` or `ERROR` | Error in test (not assertion failure) |
| `s` or `SKIPPED` | Test was skipped |
| `x` or `XFAIL` | Expected to fail, did fail |
| `X` or `XPASS` | Expected to fail, but passed |

---

## 📊 Test Coverage

### What is Coverage?

Coverage measures which lines of code are executed by tests. 100% coverage means every line was tested (but doesn't guarantee bug-free code!).

### Running with Coverage

```bash
# Run tests with coverage
pytest --cov=. --cov-report=html

# View report in terminal
pytest --cov=. --cov-report=term-missing

# Output:
# Name                  Stmts   Miss  Cover   Missing
# ---------------------------------------------------
# main.py                 150     12    92%   45-48, 112
# auth.py                  80      5    94%   67-70
# database.py              15      0   100%
# ---------------------------------------------------
# TOTAL                   245     17    93%
```

### Coverage Report

Open `htmlcov/index.html` in a browser for an interactive report:

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

---

## ✅ Best Practices

### 1. Test One Thing Per Test

```python
# ❌ Bad - testing multiple things
def test_task_operations(client, auth_headers):
    # Create
    response = client.post("/tasks", headers=auth_headers, json={...})
    assert response.status_code == 201
    
    # Update
    response = client.put("/task/1", headers=auth_headers, json={...})
    assert response.status_code == 200
    
    # Delete
    response = client.delete("/task/1", headers=auth_headers)
    assert response.status_code == 204


# ✅ Good - separate tests
def test_create_task(client, auth_headers):
    response = client.post("/tasks", headers=auth_headers, json={...})
    assert response.status_code == 201

def test_update_task(client, auth_headers, sample_task):
    response = client.put(f"/task/{sample_task.id}", ...)
    assert response.status_code == 200

def test_delete_task(client, auth_headers, sample_task):
    response = client.delete(f"/task/{sample_task.id}", ...)
    assert response.status_code == 204
```

### 2. Use Descriptive Names

```python
# ❌ Bad
def test_1():
def test_login():
def test_error():

# ✅ Good
def test_login_with_valid_credentials_returns_token():
def test_login_with_invalid_password_returns_401():
def test_create_task_without_name_returns_422():
```

### 3. Arrange-Act-Assert Pattern

```python
def test_update_task_status(client, auth_headers, sample_task):
    # Arrange - set up test data
    task_id = sample_task.id
    new_status = "completed"
    
    # Act - perform the action
    response = client.put(
        f"/task/{task_id}",
        headers=auth_headers,
        json={"status": new_status}
    )
    
    # Assert - check results
    assert response.status_code == 200
    assert response.json()["status"] == new_status
```

### 4. Use Fixtures for Common Setup

```python
# ❌ Bad - repeating setup
def test_create_task(client):
    # Login
    login_response = client.post("/token", data={...})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/tasks", headers=headers, json={...})

def test_get_tasks(client):
    # Same login code repeated...


# ✅ Good - use fixtures
def test_create_task(client, auth_headers):
    response = client.post("/tasks", headers=auth_headers, json={...})

def test_get_tasks(client, auth_headers):
    response = client.get("/tasks", headers=auth_headers)
```

### 5. Test Happy Path AND Edge Cases

```python
# Happy path
def test_create_task_success():

# Edge cases
def test_create_task_empty_name():
def test_create_task_name_too_long():
def test_create_task_invalid_status():
def test_create_task_without_auth():
def test_create_task_with_expired_token():
```

---

## 📄 Complete Test File

Here's a complete, ready-to-use test setup:

### conftest.py

```python
# tests/conftest.py
"""Pytest fixtures for Todo App tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys

# Add parent directory to path
sys.path.insert(0, '..')

from main import app
from database import get_db
from database_models import Base, UserDB, TaskDB
from auth import hash_password


# In-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Test client with test database."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Test user fixture."""
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
    """Test admin fixture."""
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
    """Auth headers for regular user."""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """Auth headers for admin user."""
    response = client.post(
        "/token",
        data={"username": "testadmin", "password": "adminpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_task(db_session, test_user):
    """Sample task fixture."""
    task = TaskDB(
        name="Sample Task",
        status="pending",
        user_id=test_user.id
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task
```

---

## 🎯 Quick Reference

### Commands Cheatsheet

```bash
# Install
pip install pytest pytest-asyncio httpx pytest-cov

# Run tests
pytest                          # All tests
pytest -v                       # Verbose
pytest -x                       # Stop on first failure
pytest -k "login"               # Filter by name
pytest --lf                     # Last failed only
pytest --cov=. --cov-report=html  # With coverage

# Create test structure
mkdir tests && touch tests/__init__.py tests/conftest.py tests/test_main.py
```

### Test Template

```python
def test_[action]_[condition]_[expected_result](client, auth_headers):
    """Description of what this test verifies."""
    # Arrange
    data = {...}
    
    # Act
    response = client.post("/endpoint", headers=auth_headers, json=data)
    
    # Assert
    assert response.status_code == expected_code
    assert response.json()["key"] == expected_value
```

---

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Real Python - Pytest Tutorial](https://realpython.com/pytest-python-testing/)
- [Testing FastAPI with async](https://www.starlette.io/testclient/)

---

<p align="center">
  Happy Testing! 🧪
</p>
