from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from Services.auth_services import authenticate_user, register_user, get_current_user, create_admin_user, verify_admin, \
    get_all_users, GetUserByID, GetUsersByEmail, EditUser, DeleteUser, reset_password, recover_password
from models import Token, User

router = APIRouter()


# Route to handle login and token generation
@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_details = authenticate_user(form_data.username, form_data.password)
    return user_details  # Returning user details along with access token


# Route for user registration
@router.post("/register")
async def register(username: str, password: str, full_name: str, email: str, role: str = "customer"):
    user_data = register_user(username=username, password=password, full_name=full_name, role=role, email=email)
    return {"message": "User registered successfully", "user": user_data}


@router.post("/admin/register")
async def register_admin(username: str, password: str, full_name: str, email: str,
                         current_user: dict = Depends(verify_admin)):
    admin_data = create_admin_user(username=username, password=password, full_name=full_name, email=email)
    return {"message": "Admin user registered successfully", "admin": admin_data}


# Route to a protected endpoint
@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {current_user['username']}, Role: {current_user['role']}"}


@router.get("/admin/users")
async def get_All_Users(current_user: dict = Depends(verify_admin)):
    return get_all_users()


@router.get("/admin/users/{id}")
async def get_user_by_id(id: str, current_user: dict = Depends(verify_admin)):
    return GetUserByID(id=id)


@router.get("/admin/users/{email}")
async def get_users_by_email(email: str, current_user: dict = Depends(verify_admin)):
    return GetUsersByEmail(email=email)


@router.patch("/admin/users/{id}")
async def edit_user(body: User, id: str, current_user: dict = Depends(verify_admin)):
    return EditUser(id=id, body=body)


@router.delete("/admin/users/{id}")
async def delete_user(id: str, current_user: dict = Depends(verify_admin)):
    return DeleteUser(id=id)


# Route for requesting password recovery
@router.post("/password/recover")
async def recover_password_route(email: str):
    return recover_password(email)


# Route for resetting password
@router.post("/password/reset")
async def reset_password_route(token: str, new_password: str):
    return reset_password(token, new_password)
