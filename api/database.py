import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "bank_management")

# Lazy client - created only when needed
_client = None

def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URI)
    return _client

def get_database() -> AsyncIOMotorDatabase:
    return get_client()[MONGODB_DB_NAME]

# Collections
def get_users_collection():
    return get_database()["users"]

def get_accounts_collection():
    return get_database()["accounts"]

def get_transactions_collection():
    return get_database()["transactions"]

# Keep these for backward compatibility
users_collection = None
accounts_collection = None
transactions_collection = None

async def ping_db() -> bool:
    await get_client().admin.command("ping")
    return True

async def ensure_indexes() -> None:
    db = get_database()
    users = db["users"]
    accounts = db["accounts"]
    transactions = db["transactions"]

    await users.create_index("username", unique=True)
    await users.create_index("email", unique=True)
    await accounts.create_index("account_number", unique=True)
    await accounts.create_index([("user_id", 1), ("created_at", -1)])
    await transactions.create_index([("account_id", 1), ("timestamp", -1)])
    await transactions.create_index([("timestamp", -1)])
