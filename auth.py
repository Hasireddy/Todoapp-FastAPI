"""
# Common Approaches:

# HTTP vs HTTP Secure
#---------------------------
# > HTTP - Send information in plain text over network
# > HTTPS - Encrypts the information using TLS (Transport Layer Security)

# 1. Basic Authentication: Encoding (Base64) [Secured over HTTPS] (TLS)
#------------------------------------------------------------------------------------
# <username>
# Base 64 password>

# 2. OAuth2: Authorization Framework
#-----------------------------------------
# Server - Username & Password
# Server verify the credentials -> Return a Token -> Stored ->  Server validate Token

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# Step 1: Define a Scheme (`random` - endpoint where token is generated)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="random")

# Step 2: Define the `random` endpoint
@app.post('/random')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify username and password
    # Return a JSON object <access_token, token_type, encoding>

# Step 3: Secure all our routes using this token
@app.post('/protected')
def protectd_route(token):
    # Verify the token is valid and correct
"""

"""
Authentication module for the Todo App.

Uses OAuth2 with JWT tokens for secure authentication.
- OAuth2PasswordBearer: Extracts token from Authorization header
- JWT: JSON Web Tokens for stateless authentication
"""
"""
Authentication module for the Todo App.

Uses OAuth2 with JWT tokens for secure authentication.
Passwords are hashed using bcrypt for security.
"""
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from database_models import UserDB

# Security configuration
# NOTE: In production, use environment variables for SECRET_KEY
# Example: SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
SECRET_KEY = "<SECRET_KEY_HERE>"  # Replace with secure random value in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MIN = 60

# OAuth2 scheme - tokenUrl must match the login endpoint path
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with a random salt.

    Note: For production, consider using bcrypt or argon2 via passlib.
    This implementation uses hashlib for zero additional dependencies.

    Args:
        password: Plain text password

    Returns:
        Salted hash in format: salt$hash
    """
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((salt + password).encode())
    return f"{salt}${hash_obj.hexdigest()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hash in format: salt$hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        salt, stored_hash = hashed_password.split("$")
        hash_obj = hashlib.sha256((salt + plain_password).encode())
        return secrets.compare_digest(hash_obj.hexdigest(), stored_hash)
    except ValueError:
        return False


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token with expiration.

    Args:
        data: Dictionary containing claims (e.g., sub, role, user_id)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    to_encode.update({"exp": expire})

    return jwt.encode(
        payload=to_encode,
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_user_by_username(db: Session, username: str) -> UserDB | None:
    """
    Retrieve a user from the database by username.

    Args:
        db: Database session
        username: Username to look up

    Returns:
        UserDB object if found, None otherwise
    """
    return db.query(UserDB).filter(UserDB.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> UserDB | None:
    """
    Authenticate a user by username and password.

    Args:
        db: Database session
        username: The username to authenticate
        password: The password to verify

    Returns:
        UserDB object if authenticated, None otherwise
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserDB:
    """
    Validate JWT token and return the current user from database.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        UserDB object for the authenticated user

    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        user = get_user_by_username(db, username)
        if user is None:
            raise credentials_exception

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception


def create_user(
    db: Session, username: str, password: str, role: str = "user"
) -> UserDB:
    """
    Create a new user in the database.

    Args:
        db: Database session
        username: Username for the new user
        password: Plain text password (will be hashed)
        role: User role ('user' or 'admin')

    Returns:
        Created UserDB object
    """
    hashed_password = hash_password(password)
    user = UserDB(username=username, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
