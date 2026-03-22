from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import CurrencyEnum
from app.models import Operation


async def create_operation(
    db: AsyncSession,
    wallet_id: int,
    type: str,
    amount: Decimal,
    currency: CurrencyEnum,
    category: str | None = None,
    subcategory: str | None = None,
) -> Operation:
    """
    Create a new operation in the database.
    
    Args:
        db: Database session
        wallet_id: Wallet id this operation belongs to
        type: Operation type (expense, income, or transfer)
        amount: Operation amount
        currency: Operation currency
        category: Operation category (optional)
        subcategory: Operation subcategory (optional)
        
    Returns:
        Created Operation instance
    """
    # Create a new Operation instance
    operation = Operation(
        wallet_id=wallet_id,  # Wallet id
        type=type,  # Operation type
        amount=amount,  # Amount
        currency=currency,  # Currency
        category=category,  # Category
        subcategory=subcategory,  # Subcategory
    )
    db.add(operation)  # Add operation to the DB session
    await db.flush()  # Flush changes (without committing)
    return operation  # Return created operation

async def get_operations_list(
    db: AsyncSession,
    wallets_ids: list[int],  # Wallet ids to filter by
    date_from: datetime | None,  # Optional start date filter
    date_to: datetime | None,  # Optional end date filter
) -> list[Operation]:
    """
    Get a list of operations from the database filtered by wallets and date range.
    
    Args:
        db: Database session
        wallets_ids: Wallet ids to filter by
        date_from: Start date filter (inclusive)
        date_to: End date filter (inclusive)
        
    Returns:
        List of operations that match the filters
    """
    stmt = select(Operation).where(Operation.wallet_id.in_(wallets_ids))

    # If start date provided, filter by operation creation date
    if date_from:
        stmt = stmt.where(Operation.created_at >= date_from)

    # If end date provided, filter by operation creation date
    if date_to:
        stmt = stmt.where(Operation.created_at <= date_to)

    # Return all matched operations
    result = await db.execute(stmt)
    return list(result.scalars().all())