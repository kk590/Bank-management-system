from datetime import datetime
import secrets

from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_active_user
from database import accounts_collection
from models import AccountCreate, AccountPublic
from serializers import serialize_account

router = APIRouter()


def generate_account_number() -> str:
    # 10-digit numeric account number
    return str(secrets.randbelow(10**10)).zfill(10)


@router.post("/", response_model=AccountPublic)
async def create_account(account: AccountCreate, current_user: dict = Depends(get_current_active_user)):
    account_doc = {
        "user_id": current_user["id"],
        "account_number": generate_account_number(),
        "account_type": account.account_type,
        "balance": float(account.initial_deposit),
        "created_at": datetime.utcnow(),
    }

    # Avoid collisions
    while await accounts_collection.find_one({"account_number": account_doc["account_number"]}):
        account_doc["account_number"] = generate_account_number()

    result = await accounts_collection.insert_one(account_doc)
    created = await accounts_collection.find_one({"_id": result.inserted_id})
    return serialize_account(created)


@router.get("/", response_model=list[AccountPublic])
async def get_my_accounts(current_user: dict = Depends(get_current_active_user)):
    cursor = accounts_collection.find({"user_id": current_user["id"]}).sort("created_at", -1)
    accounts = await cursor.to_list(length=100)
    return [serialize_account(acc) for acc in accounts]


@router.get("/{account_id}/balance")
async def get_account_balance(account_id: str, current_user: dict = Depends(get_current_active_user)):
    account = await accounts_collection.find_one({"_id": account_id})
    if not account or account.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"balance": account["balance"]}
