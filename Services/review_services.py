from datetime import datetime
from fastapi import HTTPException, status
from bson import ObjectId
from DB.db import db
from models import ReviewCreate, Review
from typing import List
from DB.db import product_db

review_db = db.reviews
# product_db = db.products


def create_review(product_id: str, review_data: ReviewCreate, username: str):
    # Check if product exists
    product = product_db.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check if user already reviewed this product
    existing_review = review_db.find_one({
        "product_id": product_id,
        "user": username
    })

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )

    # Create review document
    review = {
        "product_id": product_id,
        "user": username,
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": datetime.utcnow().isoformat()
    }

    # Insert review
    result = review_db.insert_one(review)
    review["_id"] = str(result.inserted_id)

    # Create review document for product array with string ID
    product_review = review.copy()
    product_review["_id"] = str(result.inserted_id)

    # Update product's average rating
    all_product_reviews = review_db.find({"product_id": product_id})
    total_ratings = 0
    num_reviews = 0

    for r in all_product_reviews:
        total_ratings += r["rating"]
        num_reviews += 1

    new_average = total_ratings / num_reviews if num_reviews > 0 else 0

    # Update product with new rating and add review to reviews array
    product_db.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$set": {"ratings": round(new_average, 2)},
            "$push": {"reviews": product_review}
        }
    )

    return review


def get_product_reviews(product_id: str) -> List[Review]:
    reviews = list(review_db.find({"product_id": product_id}))
    for review in reviews:
        review["_id"] = str(review["_id"])
    return [Review(**review) for review in reviews]


def get_user_reviews(username: str) -> List[Review]:
    reviews = list(review_db.find({"user": username}))
    for review in reviews:
        review["_id"] = str(review["_id"])
    return [Review(**review) for review in reviews]


def update_review(review_id: str, review_data: ReviewCreate, username: str):
    try:
        # Find the review
        review = review_db.find_one({"_id": ObjectId(review_id)})

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Check if the review belongs to the user
        if review["user"] != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reviews"
            )

        # Update review
        update_data = {
            "rating": review_data.rating,
            "comment": review_data.comment
        }

        review_db.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": update_data}
        )

        # Update product's average rating
        product_id = review["product_id"]
        all_product_reviews = review_db.find({"product_id": product_id})
        total_ratings = 0
        num_reviews = 0

        for r in all_product_reviews:
            total_ratings += r["rating"]
            num_reviews += 1

        new_average = total_ratings / num_reviews if num_reviews > 0 else 0

        # Update product rating and review in reviews array
        product_db.update_one(
            {"_id": ObjectId(product_id), "reviews._id": review_id},
            {
                "$set": {
                    "ratings": round(new_average, 2),
                    "reviews.$.rating": review_data.rating,
                    "reviews.$.comment": review_data.comment
                }
            }
        )

        # Get updated review
        updated_review = review_db.find_one({"_id": ObjectId(review_id)})
        updated_review["_id"] = str(updated_review["_id"])
        return updated_review
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating review: {str(e)}"
        )


def delete_review(review_id: str, username: str):
    try:
        # Find the review
        review = review_db.find_one({"_id": ObjectId(review_id)})

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Check if the review belongs to the user
        if review["user"] != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews"
            )

        # Delete review
        product_id = review["product_id"]
        review_db.delete_one({"_id": ObjectId(review_id)})

        # Update product's average rating
        all_product_reviews = review_db.find({"product_id": product_id})
        total_ratings = 0
        num_reviews = 0

        for r in all_product_reviews:
            total_ratings += r["rating"]
            num_reviews += 1

        new_average = total_ratings / num_reviews if num_reviews > 0 else 0

        # Update product rating and remove review from reviews array
        product_db.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$set": {"ratings": round(new_average, 2)},
                "$pull": {"reviews": {"_id": review_id}}
            }
        )

        return {"message": "Review deleted successfully", "id": review_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting review: {str(e)}"
        )