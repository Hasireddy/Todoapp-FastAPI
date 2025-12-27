# Assert Statement: Used to check a condition, if the condition fails it raises an AssertionError with the specified message
# Syntax: assert <condition>, <message>

import pytest

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
    response = client.post(
        "/register",
        json={
            "username": "test123",
            "password": "testing123",
            "role": "user",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail":"Username already registered"}

# TODO: Implement this test
def test_register_invalid_username():
    pass

# TODO: Implement this test
def test_register_invalid_password():
    pass

# TODO: Implement this test
def test_successful_login():
    pass

# TODO: Implement this test
def test_wrong_password():
    pass
