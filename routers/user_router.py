from fastapi import APIRouter, Depends

from auth import get_current_active_user
from models import UserPublic

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return current_user
