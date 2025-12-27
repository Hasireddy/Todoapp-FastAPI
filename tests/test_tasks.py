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
