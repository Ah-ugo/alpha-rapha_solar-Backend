from DB.db import subscribers_collection
from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from bson.objectid import ObjectId
from pydantic import BaseModel
from models import Product, Subscriber


# @app.post("/subscribe", status_code=status.HTTP_201_CREATED)
def subscribe(subscriber):
    if subscribers_collection.find_one({"email": subscriber.email}):
        raise HTTPException(status_code=400, detail="Email already subscribed")

    subscribers_collection.insert_one(subscriber.dict())
    return {"message": "Subscription successful"}