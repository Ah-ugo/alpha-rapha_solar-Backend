from fastapi import FastAPI
from Routers import product_routers, auth_routers

app = FastAPI()

app.include_router(product_routers.router, prefix="/products", tags=["Products"])
app.include_router(auth_routers.router, prefix="/user", tags=["Users"])