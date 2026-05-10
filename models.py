from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleEnum(str, Enum):
    customer = "customer"
    admin = "admin"


class AccountTypeEnum(str, Enum):
    savings = "savings"
    checking = "checking"


class TransactionTypeEnum(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: RoleEnum = RoleEnum.customer


class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: RoleEnum
    created_at: datetime

    model_config = ConfigDict(extra="ignore")


class AccountCreate(BaseModel):
    account_type: AccountTypeEnum
    initial_deposit: float = Field(default=0.0, ge=0.0)


class AccountPublic(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_type: AccountTypeEnum
    balance: float
    created_at: datetime

    model_config = ConfigDict(extra="ignore")


class TransactionPublic(BaseModel):
    id: str
    account_id: str
    type: TransactionTypeEnum
    amount: float
    description: str
    timestamp: datetime
    related_account_id: Optional[str] = None

    model_config = ConfigDict(extra="ignore")
