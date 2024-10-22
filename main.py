from fastapi import FastAPI
from Routers import product_routers

app = FastAPI()

app.include_router(product_routers.router, prefix="/products", tags=["Products"])