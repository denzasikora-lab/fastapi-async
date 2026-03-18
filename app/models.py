# Import Decimal for precise money calculations
from decimal import Decimal
from datetime import datetime
# Import SQLAlchemy database primitives
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

# Import declarative base
from app.database import Base
from app.enum import CurrencyEnum


# User database model
class User(Base):
    # Database table name
    __tablename__ = "user"
    # Unique user identifier (primary key)
    id: Mapped[int] = mapped_column(primary_key=True)
    # User login (unique, required)
    login: Mapped[str] = mapped_column(unique=True)


# Wallet database model
class Wallet(Base):
    # Database table name
    __tablename__ = "wallet"

    # Unique wallet identifier (primary key)
    id: Mapped[int] = mapped_column(primary_key=True)
    # Wallet name
    name: Mapped[str]
    # Wallet balance (Decimal for precision)
    balance: Mapped[Decimal]
    # Wallet owner user id (foreign key to user table)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Wallet currency (CurrencyEnum)
    currency: Mapped[CurrencyEnum]


# Money operation database model
class Operation(Base):
    # Database table name
    __tablename__ = "operation"

    # Unique operation identifier (primary key)
    id: Mapped[int] = mapped_column(primary_key=True)
    # Wallet id the operation belongs to (foreign key to wallet table)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"))
    # Operation type (expense, income, or transfer)
    type: Mapped[str]
    # Operation amount (Decimal for precision)
    amount: Mapped[Decimal]
    # Operation currency (CurrencyEnum)
    currency: Mapped[CurrencyEnum]
    # Operation category (optional, defaults to None)
    category: Mapped[str | None] = mapped_column(default=None)
    # Operation subcategory (optional, defaults to None)
    subcategory: Mapped[str | None] = mapped_column(default=None)
    # Operation creation date/time (defaults to current time)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now())
    