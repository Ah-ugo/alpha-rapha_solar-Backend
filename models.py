from pydantic import BaseModel, Field, BeforeValidator, conint
from typing import List, Optional, Annotated
from bson import ObjectId
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]

# Product Models
class ProductBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    text_specifications: Optional[str] = None
    pdf_specifications: Optional[str] = None

    class Config:
        # Use this to allow ObjectId conversion
        json_encoders = {
            ObjectId: str
        }


class ProductCreate(ProductBase):
    image_urls: Optional[List[Optional[str]]] = None


class Product(ProductCreate):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    ratings: float = 0
    reviews: Optional[List[dict]] = []


class ProductUpdate(ProductBase):
    pass


# User Models
class User(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: str = "customer"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Review Models
# class ReviewCreate(BaseModel):
#     rating: Optional[int] = None
#     comment: Optional[str] = None

class ReviewCreate(BaseModel):
    rating: conint(ge=1, le=5)  # Rating must be between 1 and 5
    comment: Optional[str] = None


class Review(ReviewCreate):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user: Optional[str] = None
    product_id: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# class Review(ReviewCreate):
#     user: Optional[str] = None
#     product_id: Optional[str] = None
#     created_at: Optional[str] = None


# Order Models
# class OrderItem(BaseModel):
#     product_id: Optional[str] = None
#     quantity: Optional[int] = None
#
#
# class OrderCreate(BaseModel):
#     items: Optional[List[OrderItem]] = []
#     user_id: Optional[str] = None
#     total_price: Optional[float] = None
#
#
# class Order(OrderCreate):
#     id: Optional[str] = None
#     status: str = "Pending"
#     created_at: Optional[str] = None

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    title: Optional[str] = None
    price: Optional[float] = None
    subtotal: Optional[float] = None

class OrderBase(BaseModel):
    items: List[OrderItem]
    total_price: Optional[float] = None
    status: str = "Pending"
    created_at: Optional[str] = None

    class Config:
        json_encoders = {
            ObjectId: str
        }

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
