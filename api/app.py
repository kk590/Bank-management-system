from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGODB_URL = os.getenv("MONGODB_URL")

client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    client = AsyncIOMotorClient(MONGODB_URL) if MONGODB_URL else None
    if client:
        db = client["bank"]
    yield
    if client:
        client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "ok"}
