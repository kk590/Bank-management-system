from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_admin_user
from database import accounts_collection, transactions_collection, users_collection
from models import AccountPublic, TransactionPublic, UserPublic
from serializers import serialize_account, serialize_transaction, serialize_user

router = APIRouter()


@router.get("/users", response_model=list[UserPublic])
async def get_all_users(current_admin: dict = Depends(get_current_admin_user)):
    users = await users_collection.find({}).sort("created_at", -1).to_list(length=1000)
    return [serialize_user(user) for user in users]


@router.get("/accounts", response_model=list[AccountPublic])
async def get_all_accounts(current_admin: dict = Depends(get_current_admin_user)):
    accounts = await accounts_collection.find({}).sort("created_at", -1).to_list(length=1000)
    return [serialize_account(acc) for acc in accounts]


@router.delete("/accounts/{account_id}")
async def delete_account(account_id: str, current_admin: dict = Depends(get_current_admin_user)):
    account = await accounts_collection.find_one({"_id": account_id})
    if not account:
        candidates = await accounts_collection.find({}).to_list(length=5000)
        account = next((a for a in candidates if str(a.get("_id")) == account_id), None)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    await accounts_collection.delete_one({"_id": account["_id"]})
    await transactions_collection.delete_many({"account_id": str(account["_id"] )})
    return {"detail": "Account and associated transactions deleted successfully"}


@router.get("/transactions", response_model=list[TransactionPublic])
async def get_all_transactions(current_admin: dict = Depends(get_current_admin_user)):
    txs = await transactions_collection.find({}).sort("timestamp", -1).to_list(length=1000)
    return [serialize_transaction(tx) for tx in txs]
