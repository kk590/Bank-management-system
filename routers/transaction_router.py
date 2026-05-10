from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_active_user
from database import accounts_collection, transactions_collection
from models import TransactionPublic, TransactionTypeEnum
from serializers import serialize_transaction

router = APIRouter()


async def get_account_or_404(account_id: str, user_id: str | None = None):
    query = {"id": account_id}  # fallback for any accidental shape
    account = await accounts_collection.find_one({"id": account_id})
    if not account:
        # real query by Mongo _id isn't practical without ObjectId import in every call; use id helper via doc fields
        account = await accounts_collection.find_one({"_id": account_id})
    if not account:
        # primary query on stored string field support if needed
        account = await accounts_collection.find_one({"account_id": account_id})
    if not account:
        # final correct query by stringified _id in user_id/account lookups cannot work if we didn't store it; so use a broader scan
        # (the routers always return serialized docs with id, while DB stores _id; call sites pass serialized id)
        candidates = await accounts_collection.find({}).to_list(length=5000)
        account = next((a for a in candidates if str(a.get("_id")) == account_id), None)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if user_id and account.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("/deposit/{account_id}", response_model=TransactionPublic)
async def deposit(account_id: str, amount: float, description: str = "Deposit", current_user: dict = Depends(get_current_active_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    account = await get_account_or_404(account_id, current_user["id"])
    new_balance = float(account["balance"]) + float(amount)
    await accounts_collection.update_one({"_id": account["_id"]}, {"$set": {"balance": new_balance}})

    tx = {
        "account_id": account_id,
        "type": TransactionTypeEnum.deposit,
        "amount": float(amount),
        "description": description,
        "timestamp": datetime.utcnow(),
    }
    result = await transactions_collection.insert_one(tx)
    created = await transactions_collection.find_one({"_id": result.inserted_id})
    return serialize_transaction(created)


@router.post("/withdraw/{account_id}", response_model=TransactionPublic)
async def withdraw(account_id: str, amount: float, description: str = "Withdrawal", current_user: dict = Depends(get_current_active_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    account = await get_account_or_404(account_id, current_user["id"])
    if float(account["balance"]) < float(amount):
        raise HTTPException(status_code=400, detail="Insufficient funds")

    new_balance = float(account["balance"]) - float(amount)
    await accounts_collection.update_one({"_id": account["_id"]}, {"$set": {"balance": new_balance}})

    tx = {
        "account_id": account_id,
        "type": TransactionTypeEnum.withdrawal,
        "amount": float(amount),
        "description": description,
        "timestamp": datetime.utcnow(),
    }
    result = await transactions_collection.insert_one(tx)
    created = await transactions_collection.find_one({"_id": result.inserted_id})
    return serialize_transaction(created)


@router.post("/transfer/{account_id}", response_model=TransactionPublic)
async def transfer(
    account_id: str,
    target_account_number: str,
    amount: float,
    description: str = "Transfer",
    current_user: dict = Depends(get_current_active_user),
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    source_account = await get_account_or_404(account_id, current_user["id"])
    target_account = await accounts_collection.find_one({"account_number": target_account_number})
    if not target_account:
        raise HTTPException(status_code=404, detail="Target account not found")
    if str(source_account["_id"]) == str(target_account["_id"]):
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")
    if float(source_account["balance"]) < float(amount):
        raise HTTPException(status_code=400, detail="Insufficient funds")

    await accounts_collection.update_one({"_id": source_account["_id"]}, {"$inc": {"balance": -float(amount)}})
    await accounts_collection.update_one({"_id": target_account["_id"]}, {"$inc": {"balance": float(amount)}})

    source_tx = {
        "account_id": account_id,
        "type": TransactionTypeEnum.transfer,
        "amount": float(amount),
        "description": f"{description} to {target_account_number}",
        "timestamp": datetime.utcnow(),
        "related_account_id": str(target_account["_id"]),
    }
    target_tx = {
        "account_id": str(target_account["_id"]),
        "type": TransactionTypeEnum.transfer,
        "amount": float(amount),
        "description": f"Transfer from {source_account['account_number']}",
        "timestamp": datetime.utcnow(),
        "related_account_id": str(source_account["_id"]),
    }

    result = await transactions_collection.insert_one(source_tx)
    await transactions_collection.insert_one(target_tx)
    created = await transactions_collection.find_one({"_id": result.inserted_id})
    return serialize_transaction(created)


@router.get("/history/{account_id}", response_model=list[TransactionPublic])
async def get_history(account_id: str, current_user: dict = Depends(get_current_active_user)):
    account = await get_account_or_404(account_id, current_user["id"])
    cursor = transactions_collection.find({"account_id": str(account["_id"]) }).sort("timestamp", -1)
    transactions = await cursor.to_list(length=200)
    return [serialize_transaction(tx) for tx in transactions]
