from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_password_hash, verify_password
from database import users_collection
from models import Token, UserCreate, UserPublic
from serializers import serialize_user

router = APIRouter()


@router.post("/register", response_model=UserPublic)
async def register(user: UserCreate):
    if await users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = user.model_dump()
    user_doc["hashed_password"] = get_password_hash(user_doc.pop("password"))
    user_doc["created_at"] = datetime.utcnow()

    result = await users_collection.insert_one(user_doc)
    created = await users_collection.find_one({"_id": result.inserted_id})
    return serialize_user(created)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user.get("role", "customer")},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
