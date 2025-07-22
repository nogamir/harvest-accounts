from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.endpoints import router
import os

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://mongo:27017")
    app.state.mongodb_client = AsyncIOMotorClient(mongodb_uri)
    app.state.mongodb = app.state.mongodb_client["accounts_db"]
    app.state.accounts_collection = app.state.mongodb["accounts"]
    print("✅ Connected to MongoDB!")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongodb_client.close()
    print("MongoDB disconnected.")

app.include_router(router)