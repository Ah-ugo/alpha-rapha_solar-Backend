from datetime import datetime
from fastapi import HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from DB.db import db
from models import OrderCreate, Order, OrderItem
from typing import List
from DB.db import product_db
from Services.auth_services import user_db

order_db = db.orders
# user_db = db.users


def create_order(order_data: OrderCreate, username: dict):
    user = user_db.find_one({"username": username["username"]})

    # Validate user existence
    if not user or "_id" not in user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in username"
        )

    total_price = 0
    order_items = []
    uid = str(user["_id"])

    for item in order_data.items:
        # Validate product ID
        try:
            product = product_db.find_one({"_id": ObjectId(item.product_id)})
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid product ID {item.product_id}"
            )

        # Check if product exists
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )

        # Check stock availability
        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product['title']}"
            )

        # Calculate item total and update total price
        item_total = product["price"] * item.quantity
        total_price += item_total

        order_items.append({
            "product_id": str(product["_id"]),
            "title": product["title"],
            "price": product["price"],
            "quantity": item.quantity,
            "subtotal": item_total
        })

        # Update product stock
        product_db.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock": -item.quantity}}
        )

    # Create the order document
    order = {
        "user_id": uid,
        "items": order_items,
        "total_price": total_price,
        "status": "Pending",  # Default status
        "created_at": datetime.utcnow().isoformat()  # Timestamp
    }

    try:
        result = order_db.insert_one(order)
        order["_id"] = str(result.inserted_id)
    except Exception as e:
        # Rollback stock updates if order creation fails
        for item in order_items:
            product_db.update_one(
                {"_id": ObjectId(item["product_id"])},
                {"$inc": {"stock": item["quantity"]}}
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )

    return order


def get_all_orders():
    order_query = order_db.find({})
    order_arr = []

    for order in order_query:
        order_arr.append(Order(**order))

    return order_arr


def get_user_orders(username: str) -> List[Order]:
    # Find the user by username
    user = user_db.find_one({"username": username})

    if not user or "_id" not in user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    try:
        # Extract user ID and find orders associated with that user
        user_id = str(user["_id"])
        orders = list(order_db.find({"user_id": user_id}).sort("created_at", -1))  # Sort orders by created_at in descending order

        # Convert ObjectId to string for each order
        for order in orders:
            order["_id"] = str(order["_id"])

        return orders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching orders: {str(e)}"
        )

def get_order_by_id(order_id: str, username: str):
    try:
        try:
            order = order_db.find_one({"_id": ObjectId(order_id)})
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid order ID {order_id}"
            )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        user_id = user_db.find_one({"username": username})
        user_id = str(user_id["_id"])

        if order["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        order["_id"] = str(order["_id"])
        return order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order: {str(e)}"
        )


def update_order_status(order_id: str, status: str, username: str):
    try:
        try:
            order = order_db.find_one({"_id": ObjectId(order_id)})
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid order ID {order_id}"
            )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )
        user_id = user_db.find_one({"username": username})
        user_id = str(user_id["_id"])

        if order["user_id"] != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        if status not in ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid order status"
            )

        # If order is being cancelled, restore product stock
        if status == "Cancelled" and order["status"] != "Cancelled":
            for item in order["items"]:
                product_db.update_one(
                    {"_id": ObjectId(item["product_id"])},
                    {"$inc": {"stock": item["quantity"]}}
                )

        # Update order status
        order_db.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status}}
        )

        # Update the local order object instead of re-fetching
        order["status"] = status
        order["_id"] = str(order["_id"])

        return order
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating order status: {str(e)}"
        )

# Handle Delete Order
def DeleteOrder(id):
    delQuery = order_db.delete_one({"_id": ObjectId(id)})

    if delQuery:
        return f"Order with id {id} deleted successfully"
    else:
        raise HTTPException(status_code=400, detail="Something went wrong")
