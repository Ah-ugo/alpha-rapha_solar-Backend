from DB.db import product_db
from models import Product, ProductCreate
from fastapi import Form, UploadFile, File, HTTPException
from typing import List
from utils.cloudinary_upload import UploadToCloudinary, UploadPdfToCloud
from models import ObjectId, Specification
from DB.db import subscribers_collection
from utils.email_reminder import send_email_reminder


def getAllProducts():
    productQuery = product_db.find({})

    prodArray = []

    for item in productQuery:
        prodArray.append(Product(**item))

    return prodArray


def create_product(
    title: str,
    description: str,
    tags: List[str],
    price: float,
    stock: int,
    category: str,
    text_specifications: List[Specification],
    pdf_specifications: UploadFile,
    image_urls: List[UploadFile]
):
    product_dict = {
        "title": title,
        "description": description,
        "tags": tags,
        "price": price,
        "stock": stock,
        "category": category,
        "text_specifications": [spec.dict() for spec in text_specifications],
        "pdf_specifications": UploadPdfToCloud(pdf_specifications),
        "image_urls": UploadToCloudinary(image_urls)
    }
    result = product_db.insert_one(product_dict)

    subscribers = subscribers_collection.find()
    subject = f"New Product Added: {product_dict['title']}"
    content = (
        f"Check out our new product:\n\n{product_dict['title']}\n\n"
        f"{product_dict['description']}\nPrice: N{product_dict['price']} https://alpharaphasolar.com/store"
    )

    # Make sure `subject` and `content` are strings before sending
    if isinstance(subject, str) and isinstance(content, str):
        for subscriber in subscribers:
            if "email" in subscriber:
                send_email_reminder(subscriber["email"], content, subject)

    created_product = product_db.find_one({"_id": result.inserted_id})
    return Product(**created_product)


def GetProductByID(id):
    get_product = product_db.find_one({"_id": ObjectId(id)})

    if get_product:
        get_product["_id"] = str(get_product["_id"])
        return get_product
    else:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")


def GetProductsByTitle(title: str):

    get_products = product_db.find({"title": {"$regex": title, "$options": "i"}})

    proArr = []

    for prods in get_products:
        prods["_id"] = str(prods["_id"])
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
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")


def DeleteProduct(id):
    delQuery = product_db.delete_one({"_id": ObjectId(id)})

    if delQuery:
        return f"Product with ID: {id} was deleted successfully"
    else:
        return "Something went wrong"
