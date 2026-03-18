from enum import StrEnum, auto


# Supported currencies
class CurrencyEnum(StrEnum):
    RUB = auto()  # Russian ruble
    USD = auto()  # US dollar
    EUR = auto()  # Euro

# Money operation types
class OperationType(StrEnum):
    EXPENSE = auto()  # Expense (spending)
    INCOME = auto()  # Income (top-up)
    TRANSFER = auto()  # Transfer between wallets