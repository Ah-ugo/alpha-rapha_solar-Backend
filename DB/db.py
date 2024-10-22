from pymongo import MongoClient

url = "mongodb+srv://parabellum:bluu12345@cluster0.5kumd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(url)
db = client.ecommerce_db
product_db = db.products
