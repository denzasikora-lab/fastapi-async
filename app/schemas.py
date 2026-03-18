# Import Decimal for precise money calculations
from datetime import datetime
from decimal import Decimal

# Import Pydantic for data models and validation

from pydantic import BaseModel, Field, field_validator

from app.enum import CurrencyEnum


# Schema describing a money operation request.
# Pydantic BaseModel validates input automatically.
class OperationRequest(BaseModel):
    # Wallet name (required, max 127 chars)
    wallet_name: str = Field(..., max_length=127)
    # Operation amount (required, must be positive)
    amount: Decimal
    # Operation description (optional, max 255 chars)
    description: str | None = Field(None, max_length=255)

    # Validator: amount must be positive
    @field_validator('amount')
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        # Ensure value is greater than zero
        if v <= 0:
            # Otherwise raise a validation error
            raise ValueError('Amount must be positive')
        # Return value if valid
        return v

    # Validator: wallet name must not be empty
    @field_validator('wallet_name')
    def wallet_name_not_empty(cls, v: str) -> str:
        # Trim whitespace
        v = v.strip()
        # Ensure non-empty string
        if not v:
            # Otherwise raise a validation error
            raise ValueError('Wallet name cannot be empty')
        # Return normalized value
        return v


# Schema for creating a wallet
class CreateWalletRequest(BaseModel):
    # Wallet name (required, max 127 chars)
    name: str = Field(..., max_length=127)
    # Initial balance (optional, defaults to 0)
    initial_balance: Decimal = 0

    # Wallet currency (defaults to RUB)
    currency: CurrencyEnum = CurrencyEnum.RUB

    # Validator: name must not be empty
    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:
        # Trim whitespace
        v = v.strip()
        # Ensure non-empty string
        if not v:
            # Otherwise raise a validation error
            raise ValueError('Wallet name cannot be empty')
        # Return normalized value
        return v

    # Validator: initial balance must not be negative
    @field_validator('initial_balance')
    def balance_not_negative(cls, v: Decimal) -> Decimal:
        # Ensure non-negative value
        if v < 0:
            # Otherwise raise a validation error
            raise ValueError('Initial balance cannot be negative')
        # Return value if valid
        return v

# Schema for creating a user
class UserRequest(BaseModel):
    # User login (required, max 127 chars)
    login: str = Field(..., max_length=127)

# Response schema with user info
class UserResponse(UserRequest):
    # Allow creating a model from object attributes (e.g., SQLAlchemy models)
    model_config = {"from_attributes": True}
    # Unique user identifier
    id: int

# Response schema with wallet info
class WalletResponse(BaseModel):
    # Allow creating a model from object attributes (e.g., SQLAlchemy models)
    model_config = {"from_attributes": True}

    # Unique wallet identifier
    id: int
    # Wallet name
    name: str
    # Wallet balance
    balance: Decimal
    # Wallet currency
    currency: CurrencyEnum

# Response schema with operation info
class OperationResponse(BaseModel):
    # Allow creating a model from object attributes (e.g., SQLAlchemy models)
    model_config = {"from_attributes": True}

    # Unique operation identifier
    id: int
    # Wallet id the operation belongs to
    wallet_id: int
    # Operation type (expense, income, or transfer)
    type: str
    # Operation amount
    amount: Decimal
    # Operation currency
    currency: CurrencyEnum
    # Operation category
    category: str | None
    # Operation subcategory
    subcategory: str | None
    # Operation creation date/time
    created_at: datetime


# Schema for creating a transfer between wallets
class TransferCreateSchema(BaseModel):
    # Wallet id to transfer from
    from_wallet_id: int
    # Wallet id to transfer to
    to_wallet_id: int
    # Transfer amount
    amount: Decimal

    # Validator: wallets must differ
    @field_validator("to_wallet_id")
    @classmethod
    def wallets_must_differ(
        cls, v: int, info
    ) -> int:
        # Ensure target wallet differs from source wallet
        if "from_wallet_id" in info.data and v == info.data["from_wallet_id"]:
            # Otherwise raise a validation error
            raise ValueError("Same wallets ids!")
        # Return value if valid
        return v

    # Validator: amount must not be negative
    @field_validator("amount")
    @classmethod
    def amount_gt_zero(cls, v: Decimal) -> Decimal:
        # Ensure non-negative value
        if v < 0:
            # Otherwise raise a validation error
            raise ValueError('Amount cannot be negative')
        # Return value if valid
        return v

class TotalBalance(BaseModel):
    total_balance: Decimal