import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "bank_management")

client = AsyncIOMotorClient(MONGODB_URI)
database: AsyncIOMotorDatabase = client[MONGODB_DB_NAME]

users_collection = database["users"]
accounts_collection = database["accounts"]
transactions_collection = database["transactions"]

async def ping_db() -> bool:
    await client.admin.command("ping")
    return True

async def ensure_indexes() -> None:
    await users_collection.create_index("username", unique=True)
    await users_collection.create_index("email", unique=True)
    await accounts_collection.create_index("account_number", unique=True)
    await accounts_collection.create_index([("user_id", 1), ("created_at", -1)])
    await transactions_collection.create_index([("account_id", 1), ("timestamp", -1)])
    await transactions_collection.create_index([("timestamp", -1)])
