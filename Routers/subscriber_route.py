from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models import Product, Subscriber
from Services.subscriber_services import subscribe

router = APIRouter(prefix="/subscribe", tags=["Subscribe"])

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_to_newsletter(subscriber: Subscriber):
    return subscribe(subscriber)