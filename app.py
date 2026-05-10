import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL")
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
from fastapi.staticfiles import StaticFiles

app = FastAPI(lifespan=lifespan)

# Change this path to your real build folder
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

@app.get("/api/health")
async def health():
    return {"status": "ok"}
