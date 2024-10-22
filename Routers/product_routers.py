from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from typing import List
from Services.product_services import getAllProducts, create_product, DeleteProduct
from models import Product

router = APIRouter()


@router.get("/")
def get_product():
    return getAllProducts()


@router.post("/")
def add_product(title: str = Form(...),
                description: str = Form(...),
                price: float = Form(...),
                stock: int = Form(...),
                category: str = Form(...),
                text_specifications: str = Form(...),
                pdf_specifications: UploadFile = File(None),
                image_urls: List[UploadFile] = File(None)):
    try:
        return create_product(title, description, price, stock, category, text_specifications, pdf_specifications,
                              image_urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add product: {str(e)}")


@router.delete("/{id}")
def delete_product(id: str):
    return DeleteProduct(id)
