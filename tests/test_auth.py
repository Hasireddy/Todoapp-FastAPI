# Assert Statement: Used to check a condition, if the condition fails it raises an AssertionError with the specified message
# Syntax: assert <condition>, <message>

import pytest

#Register a new user
def test_register_new_user(client,db_session):
    response = client.post(
        "/register",
        json={
            "username": "test123",
            "password": "testing123",
            "role": "user"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "test123"
    assert data["role"] == "user"
    assert "id" in data



# TODO: Implement this test
def test_register_duplicate_username(client,db_session):
    #Register a User
    response1 = client.post(
        "/register",
        json={
            "username": "test123",
            "password": "testing123",
            "role": "user",
        },
    )
    assert response1.status_code == 400

    #Register another user with same Username and it throws error
    response2= client.post(
        "/register",
        json={
            "username": "test123",
            "password": "testing123",
            "role": "user",
        },
    )
    assert response2.status_code == 400
    assert response2.json() == {"detail":"Username already registered"}




# TODO: Implement this test
def test_register_invalid_username(client,db_session): 
    response = client.post(
        "/register",
        json = {
            "username":"ab",
            "password":"ab123",
            "role":"user"
        },
    )
    assert response.status_code == 422
    error = response.json()["detail"][0]
    print(error)
    assert error["loc"] == ["body", "username"]
    assert "at least" in error["msg"]
   


# TODO: Implement this test
def test_register_invalid_password(client,db_session):
    response = client.post(
        "/register",
        json={"username": "validuser", "password": "123", "role": "user"},
    )
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "password"]
    assert "at least 6 characters" in error["msg"] or "ensure this value has at least" in error["msg"]


# TODO: Implement this test
def test_successful_login(client,db_session):
    # First register a user
    client.post(
        "/register",
        json={"username": "loginuser", "password": "loginpass123", "role": "user"},
    )

    # Then login
    response = client.post(
        "/token",
        data={"username": "loginuser", "password": "loginpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# TODO: Implement this test
def test_wrong_password(client, db_session):
    # Register a user
    client.post(
        "/register",
        json={"username": "wrongpassuser", "password": "correctpass", "role": "user"},
    )

    # Attempt login with wrong password
    response = client.post(
        "/token",
        data={"username": "wrongpassuser", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
