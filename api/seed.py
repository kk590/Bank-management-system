import asyncio
from datetime import datetime

from database import accounts_collection, transactions_collection, users_collection
from auth import get_password_hash


async def seed_data():
    print("Clearing existing data...")
    await users_collection.delete_many({})
    await accounts_collection.delete_many({})
    await transactions_collection.delete_many({})

    print("Creating admin user...")
    admin = {
        "username": "admin",
        "email": "admin@aureum.com",
        "hashed_password": get_password_hash("admin123"),
        "role": "admin",
        "created_at": datetime.utcnow(),
    }
    await users_collection.insert_one(admin)

    print("Creating sample customer user...")
    customer = {
        "username": "johndoe",
        "email": "john@example.com",
        "hashed_password": get_password_hash("password123"),
        "role": "customer",
        "created_at": datetime.utcnow(),
    }
    await users_collection.insert_one(customer)

    print("Seed complete.")
    print("Admin: admin / admin123")
    print("Customer: johndoe / password123")


if __name__ == "__main__":
    asyncio.run(seed_data())
