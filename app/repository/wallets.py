# Import Decimal for precise money calculations
from decimal import Decimal

# Import Session for database access
from sqlalchemy.orm import Session

from app.enum import CurrencyEnum
# Wallet model
from app.models import Wallet


# Check whether a user already has a wallet with the given name
def is_wallet_exist(db: Session, user_id: int, wallet_name: str) -> bool:
    # Query wallets table by name and user id
    return db.query(Wallet).filter(Wallet.name == wallet_name, Wallet.user_id == user_id).first() is not None


# Add income to a wallet balance
def add_income(db: Session, user_id: int, wallet_name: str, amount: Decimal) -> Wallet:
    # Find wallet by name
    wallet = db.query(Wallet).filter(Wallet.name == wallet_name, Wallet.user_id == user_id).first()
    # Add income
    wallet.balance += amount
    # Return updated wallet
    return wallet

# Get a wallet by name
def get_wallet_balance_by_name(db: Session, user_id: int, wallet_name: str) -> Wallet:
    # Query wallets table by name and user id
    return db.query(Wallet).filter(Wallet.name == wallet_name, Wallet.user_id == user_id).first()

# Subtract an expense from a wallet balance
def add_expense(db: Session, user_id: int, wallet_name: str, amount: Decimal) -> Wallet:
    # Find wallet by name
    wallet = db.query(Wallet).filter(Wallet.name == wallet_name, Wallet.user_id == user_id).first()
    # Subtract expense
    wallet.balance -= amount
    # Return updated wallet
    return wallet

# Get all wallets for a user
def get_all_wallets(db: Session, user_id: int, ) -> list[Wallet]:
    # Query wallets table by user id
    return db.query(Wallet).filter(Wallet.user_id == user_id).all()

# Create a new wallet
def create_wallet(db: Session, user_id: int, wallet_name: str, amount: Decimal, currency: CurrencyEnum) -> Wallet:
    # Create a new Wallet instance
    wallet = Wallet(name=wallet_name, balance=amount, user_id=user_id, currency=currency)
    # Add wallet to the DB session
    db.add(wallet)
    # Flush changes (without committing)
    db.flush()
    # Return created wallet
    return wallet


# Get a wallet by id
def get_wallet_by_id(db: Session, user_id: int, wallet_id: int) -> Wallet | None:
    # Query wallets table by wallet id and user id
    # scalar() returns a single value or None if not found
    return db.query(Wallet).filter(Wallet.id == wallet_id,
                                   Wallet.user_id == user_id).scalar()

