from decimal import Decimal

import pytest

from app.enum import CurrencyEnum, OperationType
from app.models import User, Wallet


@pytest.mark.asyncio
async def test_add_expense_success(db_session, client):
    # Arrange - prepare test data
    user = User(login="test")  # Create a test user
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name="card", balance=Decimal("200"), user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)

    # Act - perform the request under test
    response = await client.post(
        "/api/v1/operations/expense",  # POST request to add an expense
        json={
            "wallet_name": "card",  # Wallet name
            "amount": 50.0,  # Expense amount
            "description": "Food"  # Operation description
        },
        headers={"Authorization": f"Bearer {user.login}"}  # Auth header with user login
    )

    # Assert - verify results
    assert response.status_code == 200  # Request should succeed
    data = response.json()
    assert data["wallet_id"] == wallet.id
    assert data["type"] == OperationType.EXPENSE.value
    assert Decimal(str(data["amount"])) == Decimal("50")
    assert data["currency"] == CurrencyEnum.RUB.value
    assert data["category"] == "Food"


@pytest.mark.asyncio
async def test_add_expense_negative_amount(db_session, client):
    # Arrange - prepare test data
    user = User(login="test")  # Create a test user
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name="card", balance=Decimal("200"), user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()

    # Act - perform request with a negative amount
    response = await client.post(
        "/api/v1/operations/expense",  # POST request to add an expense
        json={
            "wallet_name": "card",  # Wallet name
            "amount": -100.0,  # Negative amount (invalid)
            "description": "Food"  # Operation description
        },
        headers={"Authorization": f"Bearer {user.login}"}  # Auth header
    )

    # Assert - should be rejected due to validation error
    assert response.status_code == 422  # 422 = validation error

@pytest.mark.asyncio
async def test_add_expense_empty_name(db_session, client):
    # Arrange - prepare test data
    user = User(login="test")  # Create a test user
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name="card", balance=Decimal("200"), user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()

    # Act - perform request with an empty wallet name
    response = await client.post(
        "/api/v1/operations/expense",  # POST request to add an expense
        json={
            "wallet_name": "   ",  # Wallet name is whitespace only (invalid)
            "amount": 100.0,  # Expense amount
            "description": "Food"  # Operation description
        },
        headers={"Authorization": f"Bearer {user.login}"}  # Auth header
    )

    # Assert - should be rejected due to validation error
    assert response.status_code == 422  # 422 = validation error


@pytest.mark.asyncio
async def test_add_expense_wallet_not_exists(db_session, client):
    # Arrange - prepare test data (create user, but do not create wallet)
    user = User(login="test")  # Create a test user
    db_session.add(user)
    await db_session.commit()

    # Act - perform request for a wallet that does not exist
    response = await client.post(
        "/api/v1/operations/expense",  # POST request to add an expense
        json={
            "wallet_name": "card",  # Wallet name that does not exist
            "amount": 100.0,  # Expense amount
            "description": "Food"  # Operation description
        },
        headers={"Authorization": f"Bearer {user.login}"}  # Auth header
    )

    # Assert - should be rejected because the wallet is missing
    assert response.status_code == 404  # 404 = not found

@pytest.mark.asyncio
async def test_add_expense_unauthorized(client):
    # Arrange - no user in database

    # Act - perform request without proper authorization
    response = await client.post(
        "/api/v1/operations/expense",  # POST request to add an expense
        json={
            "wallet_name": "card",  # Wallet name
            "amount": 100.0,  # Expense amount
            "description": "Food"  # Operation description
        },
        headers={"Authorization": f"Bearer notexists"}  # Auth header with a non-existent user
    )

    # Assert - should be rejected due to unauthorized user
    assert response.status_code == 401  # 401 = unauthorized


@pytest.mark.asyncio
async def test_add_expense_not_enough_money(db_session, client):
    # Arrange - prepare test data
    user = User(login="test")  # Create a test user
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name="card", balance=Decimal("200"), user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()

    # Act - perform request with amount greater than balance
    response = await client.post(
        "/api/v1/operations/expense",  # POST request to add an expense
        json={
            "wallet_name": "card",  # Wallet name
            "amount": 250.0,  # Expense amount greater than balance (250 > 200)
            "description": "Food"  # Operation description
        },
        headers={"Authorization": f"Bearer {user.login}"}  # Auth header
    )

    # Assert - should be rejected due to insufficient funds
    assert response.status_code == 400  # 400 = client error (insufficient funds)