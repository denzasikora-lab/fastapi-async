# Import HTTPException for HTTP error handling
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import CurrencyEnum
from app.models import User
# Import wallet repository
from app.repository import wallets as wallets_repository
# Import schemas
from app.schemas import CreateWalletRequest, WalletResponse, TotalBalance
from app.service import exchange_service

async def get_total_balance(db: AsyncSession, current_user: User) -> TotalBalance:
    """
    Compute the total balance across all user wallets, converting currencies to RUB.
    
    Args:
        db: Database session
        current_user: Current user
        
    Returns:
        Total balance in RUB
    """
    # Fetch all user wallets
    wallets = await wallets_repository.get_all_wallets(db, current_user.id)
    # Initialize accumulator
    total_balance = Decimal(0)

    # Iterate over user wallets
    for wallet in wallets:
        # If wallet currency is RUB, add directly
        if wallet.currency == CurrencyEnum.RUB:
            total_balance += wallet.balance
        else:
            # Otherwise, fetch exchange rate to RUB
            exchange_rate = await exchange_service.get_exchange_rate(wallet.currency, CurrencyEnum.RUB)
            # Convert to RUB and add
            total_balance += exchange_rate * wallet.balance

    # Return total balance in RUB
    return TotalBalance(total_balance=total_balance)

async def create_wallet(db: AsyncSession, current_user: User, wallet: CreateWalletRequest) -> WalletResponse:
    """
    Create a new wallet for a user, checking for duplicates.
    
    Args:
        db: Database session
        current_user: Current user
        wallet: Wallet creation payload (name, initial balance, currency)
        
    Returns:
        Information about the created wallet
        
    Raises:
        HTTPException: If a wallet with the same name already exists
    """
    # Ensure wallet with this name does not already exist
    if await wallets_repository.is_wallet_exist(db, current_user.id, wallet.name):
        raise HTTPException(status_code=400, detail=f"Wallet '{wallet.name}' already exists")  # Duplicate wallet -> 400

    # name and initial_balance validation is handled by CreateWalletRequest
    # Create wallet via the repository
    wallet = await wallets_repository.create_wallet(
        db, current_user.id, wallet.name, wallet.initial_balance, wallet.currency
    )
    # Persist changes
    await db.commit()
    # Return wallet info
    return WalletResponse.model_validate(wallet)


async def get_all_wallets(db: AsyncSession, current_user: User) -> list[WalletResponse]:
    """
    Get a list of all user wallets.
    
    Args:
        db: Database session
        current_user: Current user
        
    Returns:
        List of the user's wallets
    """
    # Fetch all wallets via the repository
    wallets = await wallets_repository.get_all_wallets(db, current_user.id)
    # Convert SQLAlchemy models to Pydantic response models
    return [WalletResponse.model_validate(wallet) for wallet in wallets]

