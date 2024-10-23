from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from Services.auth_services import authenticate_user, register_user, get_current_user, create_admin_user, verify_admin
from models import Token, User

router = APIRouter()

# Route to handle login and token generation
@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_details = authenticate_user(form_data.username, form_data.password)
    return user_details  # Returning user details along with access token

# Route for user registration
@router.post("/register")
async def register(username: str, password: str, full_name: str, role: str = "customer"):
    user_data = register_user(username=username, password=password, full_name=full_name, role=role)
    return {"message": "User registered successfully", "user": user_data}

@router.post("/admin/register")
async def register_admin(username: str, password: str, full_name: str, current_user: dict = Depends(verify_admin)):
    admin_data = create_admin_user(username=username, password=password, full_name=full_name)
    return {"message": "Admin user registered successfully", "admin": admin_data}

# Route to a protected endpoint
@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {current_user['username']}, Role: {current_user['role']}"}
