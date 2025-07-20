from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI()
mongodb_client = None

@app.on_event("startup")
async def startup_db_client():
    global mongodb_client
    mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://mongo:27017")
    mongodb_client = AsyncIOMotorClient(mongodb_uri)
    print("Connected to MongoDB!")

@app.on_event("shutdown")
async def shutdown_db_client():
    mongodb_client.close()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    item = await mongodb_client.test_db.test_collection.find_one({"_id": item_id})
    return {"item_id": item_id, "item": item}
