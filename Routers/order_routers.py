from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models import OrderCreate, Order
from Services.order_services import (
    create_order,
    get_user_orders,
    get_all_orders,
    get_order_by_id,
    update_order_status
)
# from fastapi.security. import JWTBearer
from Services.auth_services import get_current_user, verify_admin

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    # dependencies=[Depends(JWTBearer())]
)


@router.post("/", response_model=Order)
async def create_new_order(
        order_data: OrderCreate,
        current_user: dict = Depends(get_current_user)
):
    print(f"Current User: {current_user}")
    """
    Create a new order for the authenticated user
    """
    return create_order(order_data, current_user)


@router.get("/", response_model=List[Order])
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    """
    Get all orders for the authenticated user
    """
    return get_user_orders(current_user["username"])


@router.get("/all", response_model=List[Order])
async def get_orders(current_user: dict = Depends(verify_admin)):
    return get_all_orders()


@router.get("/{order_id}", response_model=Order)
async def get_order(
        order_id: str,
        current_user: dict = Depends(get_current_user)
):
    """
    Get a specific order by ID
    """
    return get_order_by_id(order_id, current_user["username"])


@router.patch("/{order_id}/status")
async def update_status(
        order_id: str,
        status: str,
        current_user: dict = Depends(get_current_user)
):
    """
    Update the status of an order
    """
    return update_order_status(order_id, status, current_user["username"])
