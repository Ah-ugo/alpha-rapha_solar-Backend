from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Depends
from typing import List
from Services.product_services import getAllProducts, create_product, DeleteProduct, EditProduct, GetProductByID, \
    GetProductsByTitle
from models import ProductBase
from Services.auth_services import get_current_user, verify_admin

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
                image_urls: List[UploadFile] = File(None), current_user: dict = Depends(verify_admin)):
    try:
        return create_product(title, description, price, stock, category, text_specifications, pdf_specifications,
                              image_urls)
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
