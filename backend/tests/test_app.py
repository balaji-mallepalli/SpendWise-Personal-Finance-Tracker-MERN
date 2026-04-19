import pytest
from httpx import AsyncClient



# 1. Test Health
def test_health_check(client: AsyncClient):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

import time
# 2. Test Registration limits
def test_register(client: AsyncClient):
    res = client.post("/auth/register", json={
        "email": f"newuser_{time.time()}@example.com",
        "password": "password123",
        "name": "New User"
    })
    assert res.status_code == 201
    assert "access_token" in res.json()

# 3. Test duplicate Registration
def test_register_duplicate(client: AsyncClient, test_user):
    res = client.post("/auth/register", json={
        "email": "testuser@example.com", # existing from conftest
        "password": "password123",
        "name": "Duplicate"
    })
    assert res.status_code == 400

# 4. Test Login valid
def test_login_valid(client: AsyncClient, test_user):
    res = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()

# 5. Test Login invalid
def test_login_invalid(client: AsyncClient, test_user):
    res = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401

# 6. Test JWT validation (/auth/me)
def test_me_protected(client: AsyncClient, test_user):
    token = test_user["access_token"]
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "testuser@example.com"

# 7. Test unauthorized access
def test_me_unauthorized(client: AsyncClient):
    res = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401

# 8. Test Account Creation
def test_create_account(client: AsyncClient, test_user):
    token = test_user["access_token"]
    res = client.post("/accounts/", headers={"Authorization": f"Bearer {token}"}, json={
        "name": "Test Bank",
        "type": "bank",
        "balance": 1000.50
    })
    assert res.status_code == 201
    assert res.json()["name"] == "Test Bank"
    return res.json()

# 9. Test Category Creation
def test_create_category(client: AsyncClient, test_user):
    token = test_user["access_token"]
    res = client.post("/categories/", headers={"Authorization": f"Bearer {token}"}, json={
        "name": "Test Custom Cat",
        "icon": "🚀",
        "color": "#000000"
    })
    assert res.status_code == 201
    assert res.json()["name"] == "Test Custom Cat"
    return res.json()

# 10. Test Transaction Create (Income)
def test_create_transaction_income(client: AsyncClient, test_user):
    token = test_user["access_token"]
    acc = test_create_account(client, test_user)
    cat = test_create_category(client, test_user)
    
    res = client.post("/transactions/", headers={"Authorization": f"Bearer {token}"}, json={
        "account_id": acc["id"],
        "category_id": cat["id"],
        "amount": 500.0,
        "type": "income",
        "description": "Salary Bonus",
        "date": "2023-10-01T00:00:00Z"
    })
    assert res.status_code == 201
    assert res.json()["amount"] == 500.0

# 11. Test Transaction Create (Expense & Account Balance Check)
def test_create_transaction_expense(client: AsyncClient, test_user):
    token = test_user["access_token"]
    # Get user's first account and category
    accs = client.get("/accounts/", headers={"Authorization": f"Bearer {token}"})
    cats = client.get("/categories/", headers={"Authorization": f"Bearer {token}"})
    acc_id = accs.json()[0]["id"]
    cat_id = cats.json()[0]["id"]
    
    res = client.post("/transactions/", headers={"Authorization": f"Bearer {token}"}, json={
        "account_id": acc_id,
        "category_id": cat_id,
        "amount": 100.0,
        "type": "expense",
        "description": "Groceries",
        "date": "2023-10-02T00:00:00Z"
    })
    assert res.status_code == 201
    
    # Check balance updated (-100)
    acc_check = client.get("/accounts/", headers={"Authorization": f"Bearer {token}"})
    assert acc_check.json()[0]["balance"] == 900.5 # 1000.50 - 100

# 12. Test Budget Creation
def test_create_budget(client: AsyncClient, test_user):
    token = test_user["access_token"]
    cats = client.get("/categories/", headers={"Authorization": f"Bearer {token}"})
    cat_id = cats.json()[0]["id"]
    
    res = client.post("/budgets/", headers={"Authorization": f"Bearer {token}"}, json={
        "category_id": cat_id,
        "month": 10,
        "year": 2023,
        "limit_amount": 200.0
    })
    assert res.status_code == 201
    assert res.json()["limit_amount"] == 200.0

# 13. Test Budget Status & Alerts
def test_budget_status(client: AsyncClient, test_user):
    token = test_user["access_token"]
    res = client.get("/budgets/status?month=10&year=2023", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    # Spent was 100 on a limit of 200, so % is 50
    assert data[0]["spent_amount"] == 100.0
    assert data[0]["percentage"] == 50.0

# 14. Test Alert Triggering logic
def test_alert_triggering(client: AsyncClient, test_user):
    token = test_user["access_token"]
    # Add an expense of 90 to push total spent to 190 (95% of 200 limit)
    accs = client.get("/accounts/", headers={"Authorization": f"Bearer {token}"})
    cats = client.get("/categories/", headers={"Authorization": f"Bearer {token}"})
    acc_id = accs.json()[0]["id"]
    cat_id = cats.json()[0]["id"]
    
    res = client.post("/transactions/", headers={"Authorization": f"Bearer {token}"}, json={
        "account_id": acc_id,
        "category_id": cat_id,
        "amount": 90.0,
        "type": "expense",
        "description": "More Groceries",
        "date": "2023-10-05T00:00:00Z"
    })
    assert res.status_code == 201
    
    # Check dashboard for triggered alerts
    dash = client.get("/dashboard/summary?month=10&year=2023", headers={"Authorization": f"Bearer {token}"})
    assert dash.status_code == 200
    assert dash.json()["active_alerts"] >= 1

# 15. Test CSV Export
def test_export_csv(client: AsyncClient, test_user):
    token = test_user["access_token"]
    res = client.get("/transactions/export", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "text/csv; charset=utf-8"
    content = res.content.decode()
    assert "Date,Type,Category,Account,Amount,Description" in content
    assert "100.0" in content
