from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.openapi.docs import get_swagger_ui_html
from Routers import product_routers, auth_routers, review_routers, order_routers, subscriber_route, project_routers

app = FastAPI(
    title="Alpha-Rapha Solar",
    description="Alpha-Rapha solar API documentation developed by Ahuekwe Prince Ugochukwu.",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(product_routers.router, prefix="/products", tags=["Products"])
app.include_router(project_routers.router, prefix="/projects", tags=["Projects"])
app.include_router(auth_routers.router, prefix="/user", tags=["Users"])
app.include_router(review_routers.router)
app.include_router(order_routers.router)
app.include_router(subscriber_route.router)
