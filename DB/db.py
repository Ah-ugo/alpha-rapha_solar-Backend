from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("MONGO_URL")
client = MongoClient(url)
db = client.ecommerce_db
product_db = db.products
projects_db = db.projects
subscribers_collection = db.subscribers
