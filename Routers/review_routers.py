from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models import ReviewCreate, Review
from Services.review_services import (
    create_review,
    get_product_reviews,
    get_user_reviews,
    update_review,
    delete_review
)
from Services.auth_services import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/{product_id}", response_model=Review)
async def add_review(
    product_id: str,
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new review for a product.
    Requires authentication.
    """
    return create_review(product_id, review, current_user["username"])

@router.get("/product/{product_id}", response_model=List[Review])
async def list_product_reviews(product_id: str):
    """
    Get all reviews for a specific product.
    No authentication required.
    """
    return get_product_reviews(product_id)

@router.get("/user/me", response_model=List[Review])
async def list_user_reviews(current_user: dict = Depends(get_current_user)):
    """
    Get all reviews by the current user.
    Requires authentication.
    """
    return get_user_reviews(current_user["username"])

@router.put("/{review_id}", response_model=Review)
async def modify_review(
    review_id: str,
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing review.
    Requires authentication and ownership of the review.
    """
    return update_review(review_id, review, current_user["username"])

@router.delete("/{review_id}")
async def remove_review(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a review.
    Requires authentication and ownership of the review.
    """
    return delete_review(review_id, current_user["username"])