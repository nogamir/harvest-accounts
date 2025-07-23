from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.endpoints import router
from mongo_db.shared import (
    MONGODB_URI, ACCOUNTS_DB_NAME, ACCOUNTS_COLLECTION_NAME
)

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    app.state.mongodb_client = AsyncIOMotorClient(MONGODB_URI)
    app.state.mongodb = app.state.mongodb_client[ACCOUNTS_DB_NAME]
    app.state.accounts_collection = app.state.mongodb[ACCOUNTS_COLLECTION_NAME]
    print("Connected to MongoDB!")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongodb_client.close()
    print("MongoDB disconnected.")

app.include_router(router)