from DB.db import product_db
from models import Product, ProductCreate
from fastapi import Form, UploadFile, File, HTTPException
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

def GetProductByID(id):
    get_product = product_db.find_one({"_id": ObjectId(id)})

    if get_product:
        get_product["_id"] = str(get_product["_id"])
        return get_product
    else:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")


def GetProductsByTitle(title: str):
    # Use a case-insensitive regular expression to match titles containing the search string
    get_products = product_db.find({"title": {"$regex": title, "$options": "i"}})

    proArr = []

    for prods in get_products:
        prods["_id"] = str(prods["_id"])  # Convert ObjectId to string
        proArr.append(Product(**prods))

    if not proArr:
        raise HTTPException(status_code=404, detail=f"No products found containing '{title}'")

    return proArr

def EditProduct(id, body):
    update_data = {k: v for k, v in body.dict().items() if v is not None}
    get_product = product_db.find_one({"_id": ObjectId(id)})
    if get_product:
        product_db.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        get_product = product_db.find_one({"_id": ObjectId(id)})
        get_product["_id"] = str(get_product["_id"])
        return get_product
    else:
        raise HTTPException(status_code=404, detail=f"shop with id {id} not found")


def DeleteProduct(id):
    delQuery = product_db.delete_one({"_id": ObjectId(id)})

    if delQuery:
        return f"Product with ID: {id} was deleted successfully"
    else:
        return "Something went wrong"
