from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routers import product_routers, auth_routers, review_routers,order_routers, subscriber_route

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_routers.router, prefix="/products", tags=["Products"])
app.include_router(auth_routers.router, prefix="/user", tags=["Users"])
app.include_router(review_routers.router)
app.include_router(order_routers.router)
app.include_router(subscriber_route.router)