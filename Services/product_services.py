from DB.db import product_db
from models import Product, ProductCreate
from fastapi import Form, UploadFile, File
from typing import List
from utils.cloudinary_upload import UploadToCloudinary, UploadPdfToCloud
from models import ObjectId


def getAllProducts():
    productQuery = product_db.find({})

    prodArray = []

    for item in productQuery:
        prodArray.append(Product(**item))

    return prodArray


def create_product(title,
                   description,
                   price,
                   stock,
                   category,
                   text_specifications,
                   pdf_specifications,
                   image_urls):
    product_dict = {
        "title": title,
        "description": description,
        "price": price,
        "stock": stock,
        "category": category,
        "text_specifications": text_specifications,
        "pdf_specifications": UploadPdfToCloud(pdf_specifications),
        "image_urls": UploadToCloudinary(image_urls)
    }
    # Insert the product into the collection
    result = product_db.insert_one(product_dict)
    # Fetch the created product with its ID
    created_product = product_db.find_one({"_id": result.inserted_id})
    return Product(**created_product)  # Convert the fetched document to Product model


def DeleteProduct(id):
    delQuery = product_db.delete_one({"_id": ObjectId(id)})

    if delQuery:
        return f"Product with ID: {id} was deleted successfully"
    else:
        return "Something went wrong"
