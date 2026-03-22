# Import APIRouter to define API endpoints
from datetime import datetime  # Import datetime for date filtering

from fastapi import APIRouter, Depends, Query  # Endpoint definitions and dependency injection
from sqlalchemy.ext.asyncio import AsyncSession

# Import dependencies for DB session and auth
from app.dependency import get_db, get_current_user
from app.models import User  # Import the User model
# Import schemas for money operations
from app.schemas import OperationRequest, OperationResponse, TransferCreateSchema
# Import the operations service
from app.service import operations as operations_service

# Router for operations-related endpoints
router = APIRouter()

@router.post("/operations/income", response_model=OperationResponse)
async def add_income(operation: OperationRequest, db: AsyncSession = Depends(get_db),  # DB session via dependency injection
                current_user: User = Depends(get_current_user)):  # Current user from auth token
    # Delegate to the service to add income to the wallet balance
    return await operations_service.add_income(db, current_user, operation)


@router.post("/operations/expense", response_model=OperationResponse)
async def add_expense(operation: OperationRequest, db: AsyncSession = Depends(get_db),  # DB session via dependency injection
                current_user: User = Depends(get_current_user)):  # Current user from auth token
    # Delegate to the service to add an expense (subtract from wallet balance)
    return await operations_service.add_expense(db, current_user, operation)

@router.get("/operations", response_model=list[OperationResponse])
async def get_operations_list(
    wallet_id: int | None = Query(None),  # Optional wallet id filter
    date_from: datetime | None = Query(None),  # Optional start date filter
    date_to: datetime | None = Query(None),  # Optional end date filter
    user: User = Depends(get_current_user),  # Current user from auth token
    db: AsyncSession = Depends(get_db),  # DB session
):
    # Delegate to the service to fetch the filtered list
    return await operations_service.get_operations_list(db, user, wallet_id, date_from, date_to)


@router.post("/operations/transfer", response_model=OperationResponse)
async def create_transfer(
    payload: TransferCreateSchema,  # Transfer payload between wallets
    user: User = Depends(get_current_user),  # Current user from auth token
    db: AsyncSession = Depends(get_db),  # DB session via dependency injection
):
    # Delegate to the service to transfer money (with currency conversion when needed)
    return await operations_service.transfer_between_wallets(
        db,  # DB session
        user.id,  # User id
        payload.from_wallet_id,  # Sender wallet id
        payload.to_wallet_id,  # Recipient wallet id
        payload.amount,  # Transfer amount
    )
