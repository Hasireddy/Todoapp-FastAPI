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
