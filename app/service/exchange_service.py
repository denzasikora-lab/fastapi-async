from decimal import Decimal
from typing import Dict, Tuple
import aiohttp

from app.enum import CurrencyEnum

# Fallback exchange rates used when the external API is unavailable.
# Key: tuple of (base currency, target currency)
# Value: exchange rate
FALLBACK_RATES: Dict[Tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal(str(95.0)),  # USD->RUB exchange rate
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal(str(0.92)),  # USD->EUR exchange rate
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal(str(103.26)),  # EUR->RUB exchange rate
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal(str(0.0105)),  # RUB->USD exchange rate
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal(str(1.087)),  # EUR->USD exchange rate
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal(str(0.0097)),  # RUB->EUR exchange rate
}


async def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:
    """
    Get an exchange rate between two currencies from an external API or the fallback map.
    
    Args:
        base: Base currency (the currency to convert from)
        target: Target currency (the currency to convert to)
        
    Returns:
        Exchange rate (how many units of target currency for one unit of base currency).
        If a rate cannot be resolved, returns 1 (no conversion).
    """
    # Build the external API URL for exchange rates
    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json"

    # Request timeout (5 seconds)
    timeout = aiohttp.ClientTimeout(total=5.0)

    try:
        # Create an async HTTP client session
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Perform GET request to the exchange-rate API
            async with session.get(url) as response:
                # Ensure request succeeded
                response.raise_for_status()
                # Parse JSON response
                data = await response.json()
                # Extract the rate map for the base currency
                base_map = data.get(base, {})
                # Get rate for the target currency
                rate = base_map.get(target)

        # If rate is found and numeric, return it
        if rate is not None and isinstance(rate, (int, float)):
            return Decimal(rate)
        # If no rate is found, raise to use fallback logic
        raise KeyError('Rate not found')

    except Exception:
        # If the external API is unavailable, use fallback rates.
        # If no rate is found, return 1 (no conversion).
        return FALLBACK_RATES.get((base, target), Decimal(1))