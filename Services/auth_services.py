from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from passlib.context import CryptContext
# from pymongo.collection import Collection
from bson import ObjectId
from DB.db import db
from models import User
from utils.email_reminder import send_email_reminder

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
def register_user(username: str, password: str, full_name: str, email: str, role: str = "customer"):
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
        "email": email,
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
def create_admin_user(username: str, password: str, full_name: str, email: str):
    # This function allows only developers to create admin users
    hashed_password = hash_password(password)

    admin_data = {
        "username": username,
        "full_name": full_name,
        "email": email,
        "password": hashed_password,
        "role": "admin",  # Explicitly set the admin role
        "created_at": datetime.utcnow(),
    }

    # Insert the new admin data into the database
    result = user_db.insert_one(admin_data)

    # Add the _id to the admin_data dictionary and convert it to a string
    admin_data["_id"] = str(result.inserted_id)

    # Remove the hashed password from the returned response
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
        # "email": user["email"],
        "role": user["role"],
        "access_token": access_token,
        "token_type": "bearer",
    }

    if "email" in user:
        user_details["email"] = user["email"]

    return user_details


# For user management
def get_all_users():
    all_users_query = user_db.find({})
    userArr = []

    for user in all_users_query:
        userArr.append(User(**user))
    return userArr


def GetUserByID(id):
    get_user = user_db.find_one({"_id": ObjectId(id)})

    if get_user:
        get_user["_id"] = str(get_user["_id"])
        return get_user
    else:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")


def GetUsersByEmail(email: str):
    # Use a case-insensitive regular expression to match titles containing the search string
    get_users = user_db.find({"email": {"$regex": email, "$options": "i"}})

    userArr = []

    for users in get_users:
        users["_id"] = str(users["_id"])  # Convert ObjectId to string
        userArr.append(User(**users))

    if not userArr:
        raise HTTPException(status_code=404, detail=f"No Users found containing '{email}'")

    return userArr

def EditUser(id, body):
    update_data = {k: v for k, v in body.dict().items() if v is not None}
    get_user = user_db.find_one({"_id": ObjectId(id)})
    if get_user:
        user_db.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        get_user = user_db.find_one({"_id": ObjectId(id)})
        get_user["_id"] = str(get_user["_id"])
        return get_user
    else:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")


def DeleteUser(id):
    delQuery = user_db.delete_one({"_id": ObjectId(id)})

    if delQuery:
        return f"User with ID: {id} was deleted successfully"
    else:
        return "Something went wrong"


# Password Reset Functions

def create_password_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError()
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )


def recover_password(email: str):
    user = user_db.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found",
        )

    # Generate password reset token
    reset_token = create_password_reset_token(email)

    # Create the email message
    message = f"Click on the link to reset your password: https://alpharaphasolar-nine.vercel.app/reset-password?token={reset_token}"

    # Send the email
    send_email_reminder(email, message)

    return {"message": "Password reset link sent to your email."}


def reset_password(token: str, new_password: str):
    email = verify_password_reset_token(token)

    user = user_db.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Hash the new password (you should already have hash_password function)
    hashed_password = hash_password(new_password)

    # Update the user's password in the database
    user_db.update_one({"email": email}, {"$set": {"password": hashed_password}})

    return {"message": "Password reset successful."}