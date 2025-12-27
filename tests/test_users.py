import pytest

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
