from decimal import Decimal

from app.models import User, Wallet


def test_add_expense_success(db_session, client):
    # Arrange - prepare test data
    user = User(login="test")  # Create a test user
    db_session.add(user)  # Add user to the DB session
    db_session.flush()  # Flush without commit (to obtain user.id)
    wallet = Wallet(name="card", balance=200, user_id=user.id)  # Create wallet with balance 200
    db_session.add(wallet)  # Add wallet to the session
    db_session.commit()  # Persist changes
    db_session.refresh(wallet)  # Refresh wallet from DB

    # Act - perform the request under test
    response = client.post(
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
    assert response.json()["message"] == "Expense added"  # Success message
    assert response.json()["wallet"] == wallet.name  # Wallet name in response
    assert Decimal(str(response.json()["amount"])) == Decimal(50)  # Expense amount (Decimal for precision)
    assert Decimal(str(response.json()["new_balance"])) == Decimal(150)  # New balance (200 - 50 = 150)
    assert response.json()["description"] == "Food"  # Operation description


def test_add_expense_negative_amount(db_session, client):
    # Arrange - prepare test data
    user = User(login="test")  # Create a test user
    db_session.add(user)  # Add user to session
    db_session.flush()  # Flush without commit
    wallet = Wallet(name="card", balance=200, user_id=user.id)  # Create wallet with balance 200
    db_session.add(wallet)  # Add wallet to the session
    db_session.commit()  # Persist changes
    db_session.refresh(wallet)  # Refresh wallet from DB

    # Act - perform request with a negative amount
    response = client.post(
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

def test_add_expense_empty_name(db_session, client):
    # Arrange - prepare test data
    user = User(login="test")  # Create a test user
    db_session.add(user)  # Add user to session
    db_session.flush()  # Flush without commit
    wallet = Wallet(name="card", balance=200, user_id=user.id)  # Create wallet with balance 200
    db_session.add(wallet)  # Add wallet to the session
    db_session.commit()  # Persist changes
    db_session.refresh(wallet)  # Refresh wallet from DB

    # Act - perform request with an empty wallet name
    response = client.post(
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


def test_add_expense_wallet_not_exists(db_session, client):
    # Arrange - prepare test data (create user, but do not create wallet)
    user = User(login="test")  # Create a test user
    db_session.add(user)  # Add user to the session
    db_session.commit()  # Persist changes

    # Act - perform request for a wallet that does not exist
    response = client.post(
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

def test_add_expense_unauthorized(client):
    # Arrange - no user in database

    # Act - perform request without proper authorization
    response = client.post(
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


def test_add_expense_not_enough_money(db_session, client):
    # Arrange - prepare test data
    user = User(login="test")  # Create a test user
    db_session.add(user)  # Add user to session
    db_session.flush()  # Flush without commit
    wallet = Wallet(name="card", balance=200, user_id=user.id)  # Create wallet with balance 200
    db_session.add(wallet)  # Add wallet to the session
    db_session.commit()  # Persist changes
    db_session.refresh(wallet)  # Refresh wallet from DB

    # Act - perform request with amount greater than balance
    response = client.post(
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