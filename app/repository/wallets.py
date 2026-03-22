# Import Decimal for precise money calculations
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import CurrencyEnum
# Wallet model
from app.models import Wallet


# Check whether a user already has a wallet with the given name
async def is_wallet_exist(db: AsyncSession, user_id: int, wallet_name: str) -> bool:
    stmt = select(Wallet.id).where(Wallet.name == wallet_name, Wallet.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


# Add income to a wallet balance
async def add_income(db: AsyncSession, user_id: int, wallet_name: str, amount: Decimal) -> Wallet:
    wallet = await get_wallet_balance_by_name(db, user_id, wallet_name)
    # Add income
    wallet.balance += amount
    # Return updated wallet
    return wallet

# Get a wallet by name
async def get_wallet_balance_by_name(db: AsyncSession, user_id: int, wallet_name: str) -> Wallet | None:
    stmt = select(Wallet).where(Wallet.name == wallet_name, Wallet.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# Subtract an expense from a wallet balance
async def add_expense(db: AsyncSession, user_id: int, wallet_name: str, amount: Decimal) -> Wallet:
    wallet = await get_wallet_balance_by_name(db, user_id, wallet_name)
    # Subtract expense
    wallet.balance -= amount
    # Return updated wallet
    return wallet

# Get all wallets for a user
async def get_all_wallets(db: AsyncSession, user_id: int) -> list[Wallet]:
    stmt = select(Wallet).where(Wallet.user_id == user_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())

# Create a new wallet
async def create_wallet(db: AsyncSession, user_id: int, wallet_name: str, amount: Decimal, currency: CurrencyEnum) -> Wallet:
    # Create a new Wallet instance
    wallet = Wallet(name=wallet_name, balance=amount, user_id=user_id, currency=currency)
    # Add wallet to the DB session
    db.add(wallet)
    # Flush changes (without committing)
    await db.flush()
    # Return created wallet
    return wallet


# Get a wallet by id
async def get_wallet_by_id(db: AsyncSession, user_id: int, wallet_id: int) -> Wallet | None:
    stmt = select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

