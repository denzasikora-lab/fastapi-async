# Import APIRouter to define API endpoints
from fastapi import APIRouter, Depends  # Endpoint definitions and dependency injection
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db, get_current_user
from app.models import User  # Import the User model
# Import schema for wallet creation
from app.schemas import CreateWalletRequest, WalletResponse
# Import the wallets service
from app.service import wallets as wallets_service

# Router for wallet-related endpoints
router = APIRouter()

@router.get("/balance")
async def get_balance(db: AsyncSession = Depends(get_db),  # DB session via dependency injection
                current_user: User = Depends(get_current_user)):  # Current user from auth token
    # Delegate to the service to compute the total balance
    return await wallets_service.get_total_balance(db, current_user)  # If wallet_name is None, return total balance

@router.post("/wallets", response_model=WalletResponse)
async def create_wallet(wallet: CreateWalletRequest, db: AsyncSession = Depends(get_db),  # DB session via dependency injection
                current_user: User = Depends(get_current_user)):  # Current user from auth token
    # Delegate to the service to create a new wallet
    return await wallets_service.create_wallet(db, current_user, wallet)


@router.get("/wallets", response_model=list[WalletResponse])
async def get_all_wallets(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):  # DB session and current user via dependency injection
    # Delegate to the service to fetch all user wallets
    return await wallets_service.get_all_wallets(db, current_user)
