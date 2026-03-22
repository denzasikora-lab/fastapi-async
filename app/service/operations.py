# Import HTTPException for HTTP error handling
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import OperationType
from app.models import User
# Import schemas for money operations
from app.schemas import OperationRequest, OperationResponse
# Import repositories
from app.repository import wallets as wallets_repository
from app.repository import operations as operations_repository
from app.service.exchange_service import get_exchange_rate


async def add_income(db: AsyncSession, current_user: User, operation: OperationRequest) -> OperationResponse:
    """
    Add income to a wallet balance, validating that the wallet exists.
    
    Args:
        db: Database session
        current_user: Current user
        operation: Operation data (wallet name, amount, description)
        
    Returns:
        Information about the created income operation
        
    Raises:
        HTTPException: If the wallet is not found
    """
    # Ensure the wallet exists
    if not await wallets_repository.is_wallet_exist(db, current_user.id, operation.wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{operation.wallet_name}' not found"
        )  # Wallet not found -> 404

    # amount > 0 validation is handled by OperationRequest
    # Add income to the wallet balance via the repository
    wallet = await wallets_repository.add_income(db, current_user.id, operation.wallet_name, operation.amount)
    # Create an income operation record via the repository
    operation_row = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,  # Wallet id
        type=OperationType.INCOME,  # Operation type
        amount=operation.amount,  # Amount
        currency=wallet.currency,  # Currency (from wallet)
        category=operation.description,  # Category (from description)
    )
    # Persist changes
    await db.commit()
    # Return operation info
    return OperationResponse.model_validate(operation_row)

async def add_expense(db: AsyncSession, current_user: User, operation: OperationRequest) -> OperationResponse:
    """
    Subtract an expense from a wallet balance, validating that the wallet exists and has enough funds.
    
    Args:
        db: Database session
        current_user: Current user
        operation: Operation data (wallet name, amount, description)
        
    Returns:
        Information about the created expense operation
        
    Raises:
        HTTPException: If the wallet is not found or there are insufficient funds
    """
    # Ensure the wallet exists
    if not await wallets_repository.is_wallet_exist(db, current_user.id, operation.wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{operation.wallet_name}' not found"
        )  # Wallet not found -> 404

    # amount > 0 validation is handled by OperationRequest

    # Check if there are enough funds (business logic, not validation!)
    # Get current wallet balance via the repository
    wallet = await wallets_repository.get_wallet_balance_by_name(db, current_user.id, operation.wallet_name)
    if wallet is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")
    if wallet.balance < operation.amount:  # Balance is less than the expense amount
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {wallet.balance}"
        )  # Not enough money -> 400

    # Subtract expense from wallet balance via the repository
    wallet = await wallets_repository.add_expense(db, current_user.id, operation.wallet_name, operation.amount)
    # Create an expense operation record via the repository
    operation_row = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,  # Wallet id
        type=OperationType.EXPENSE,  # Operation type
        amount=operation.amount,  # Amount
        currency=wallet.currency,  # Currency (from wallet)
        category=operation.description,  # Category (from description)
    )
    # Persist changes
    await db.commit()
    # Return operation info
    return OperationResponse.model_validate(operation_row)


async def get_operations_list(
    db: AsyncSession,
    current_user: User,
    wallet_id: int | None = None,  # Optional wallet id filter
    date_from: datetime | None = None,  # Optional start date filter
    date_to: datetime | None = None  # Optional end date filter
) -> list[OperationResponse]:
    """
    Get a user's operations, optionally filtered by wallet and date range.
    
    Args:
        db: Database session
        current_user: Current user
        wallet_id: Wallet id to filter by (if omitted, returns operations for all wallets)
        date_from: Start date for filtering
        date_to: End date for filtering
        
    Returns:
        List of operations as OperationResponse
        
    Raises:
        HTTPException: If the specified wallet is not found
    """
    # If a wallet id is provided, filter by that wallet
    if wallet_id:
        # Fetch the wallet via the repository
        wallet = await wallets_repository.get_wallet_by_id(db, current_user.id, wallet_id)
        # Ensure the wallet exists
        if not wallet:
            raise HTTPException(
                status_code=404,
                detail=f"Wallet '{wallet_id}' not found"
            )  # Wallet not found -> 404

        # Filter operations by the specified wallet only
        wallets_ids = [wallet.id]
    else:
        # Otherwise, include all user wallets
        wallets = await wallets_repository.get_all_wallets(db, current_user.id)
        # Build the list of wallet ids
        wallets_ids = [w.id for w in wallets]

    # Fetch operations list from the repository with filters
    operations = await operations_repository.get_operations_list(
        db,
        wallets_ids,  # Wallet ids to filter by
        date_from,  # Start date filter
        date_to  # End date filter
    )
    # Convert SQLAlchemy models to Pydantic response models
    result = []
    for operation in operations:
        result.append(OperationResponse.model_validate(operation))
    return result


async def transfer_between_wallets(
    db: AsyncSession, user_id: int, from_wallet_id: int, to_wallet_id: int, amount: Decimal,
) -> OperationResponse:
    """
    Transfer money between a user's wallets with currency conversion when needed.
    
    Args:
        db: Database session
        user_id: User id
        from_wallet_id: Sender wallet id
        to_wallet_id: Recipient wallet id
        amount: Transfer amount
        
    Returns:
        Information about the created transfer operation
        
    Raises:
        HTTPException: If a wallet is not found or there are insufficient funds
    """
    # Fetch the sender wallet via the repository
    from_wallet = await wallets_repository.get_wallet_by_id(db, user_id, from_wallet_id)
    # Fetch the recipient wallet via the repository
    to_wallet = await wallets_repository.get_wallet_by_id(db, user_id, to_wallet_id)

    # Ensure both wallets exist
    if not from_wallet or not to_wallet:
        raise HTTPException(404, "Wallet not Found")  # Missing wallet -> 404

    # Ensure the sender wallet has enough funds
    if from_wallet.balance < amount:
        raise HTTPException(
            400,
            f"Not enough money: {from_wallet.balance} {from_wallet.currency}",
        )  # Not enough money -> 400

    # By default, recipient amount equals the requested transfer amount
    target_amount = amount
    # If wallet currencies differ, convert
    if from_wallet.currency != to_wallet.currency:
        # Fetch the exchange rate
        exchange_rate = await get_exchange_rate(
            from_wallet.currency, to_wallet.currency
        )
        # Convert the amount using the exchange rate
        target_amount = amount * exchange_rate

    # Subtract from sender wallet
    from_wallet.balance = from_wallet.balance - amount
    # Add to recipient wallet (after conversion if needed)
    to_wallet.balance = to_wallet.balance + target_amount
    # Create a transfer operation record via the repository
    operation_row = await operations_repository.create_operation(
        db=db,
        wallet_id=from_wallet.id,  # Sender wallet id
        type=OperationType.TRANSFER,  # Operation type
        amount=target_amount,  # Amount (after conversion if applicable)
        currency=to_wallet.currency,  # Currency
        category="transfer",  # Operation category
    )
    db.add(from_wallet)  # Add updated sender wallet to the session
    db.add(to_wallet)  # Add updated recipient wallet to the session
    db.add(operation_row)  # Add operation to the session
    await db.commit()  # Persist changes
    return OperationResponse.model_validate(operation_row)  # Return operation info
