import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = mongodb+srv://bankadmin:<db_password>@cluster0.sg6au3d.mongodb.net/?appName=Cluster0
client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    if not MONGODB_URL:
        raise RuntimeError("MONGODB_URL is missing")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["bankdb"]
    yield
    client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "ok"}
