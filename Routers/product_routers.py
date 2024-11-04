from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Depends
from typing import List
from Services.product_services import getAllProducts, create_product, DeleteProduct, EditProduct, GetProductByID, \
    GetProductsByTitle
from models import ProductBase, Specification
from Services.auth_services import get_current_user, verify_admin
import json

router = APIRouter()


@router.get("/")
def get_product():
    return getAllProducts()


@router.post("/")
def add_product(
    title: str = Form(...),
    description: str = Form(...),
    tags: List[str] = Form(...),  # Use "Add item" in Swagger for multiple tags
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(...),
    text_specifications: str = Form(...),  # Accept JSON string
    pdf_specifications: UploadFile = File(None),
    image_urls: List[UploadFile] = File(None),  # Use "Add item" in Swagger for multiple images
    current_user: dict = Depends(verify_admin)
):
    try:
        # Convert the JSON string for text_specifications into a list of Specification objects
        specifications_list = [Specification(**item) for item in json.loads(text_specifications)]

        # Call the create_product function with parsed data
        return create_product(
            title, description, tags, price, stock, category,
            specifications_list, pdf_specifications, image_urls
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add product: {str(e)}")


@router.get("/{id}")
def get_product_by_id(id: str):
    return GetProductByID(id)


@router.get("/title/{title}")
def get_product_by_title(title: str):
    return GetProductsByTitle(title)


@router.patch("/{id}")
def edit_product(id: str, body: ProductBase, current_user: dict = Depends(verify_admin)):
    return EditProduct(id=id, body=body)


@router.delete("/{id}")
def delete_product(id: str, current_user: dict = Depends(verify_admin)):
    return DeleteProduct(id)
