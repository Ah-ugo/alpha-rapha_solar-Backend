from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from passlib.context import CryptContext
# from pymongo.collection import Collection
from bson import ObjectId
from DB.db import db  # Assuming you have `db.py` as your MongoDB connection module

# Constants
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB Collections
user_db = db.users  # Reference to the 'users' collection

# Exception to raise if credentials are invalid
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# Create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Create user token with roles
def create_user_token(username: str, role: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "role": role}, expires_delta=access_token_expires
    )
    return access_token


# Verify token and get user
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return {"username": username, "role": role}
    except JWTError:
        raise credentials_exception


# Dependency to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)


# Password hashing and verification functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Function to register a new user
def register_user(username: str, password: str, full_name: str, role: str = "customer"):
    # Check if the username already exists
    if user_db.find_one({"username": username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    hashed_password = hash_password(password)

    # Insert new user into the database
    user_data = {
        "username": username,
        "full_name": full_name,
        "password": hashed_password,
        "role": role,  # Assign the role during registration
        "created_at": datetime.utcnow(),
    }

    # Insert into the database and get the inserted ID
    result = user_db.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string
    user_data.pop("password")  # Remove password before returning

    return user_data


# Function for developers to create admin users
def create_admin_user(username: str, password: str, full_name: str):
    # This function allows only developers to create admin users
    hashed_password = hash_password(password)

    admin_data = {
        "username": username,
        "full_name": full_name,
        "password": hashed_password,
        "role": "admin",  # Explicitly set the admin role
        "created_at": datetime.utcnow(),
    }

    user_db.insert_one(admin_data)
    admin_data.pop("password")

    return admin_data


async def verify_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None or role is None:
            raise credentials_exception
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

# Function to authenticate user (login)
def authenticate_user(username: str, password: str):
    user = user_db.find_one({"username": username})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate token
    access_token = create_user_token(username=username, role=user["role"])

    # Return user details along with the access token
    user_details = {
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "access_token": access_token,
        "token_type": "bearer",
    }
    return user_details
