import pytest
from httpx import AsyncClient, ASGITransport
import os
import asyncio

# Setup mocked DB for tests
os.environ["MONGODB_URL"] = "mongodb://localhost:27017" # Ensure tests run against local DB
from app.main import app
from app.database import connect_db, close_db, get_db

from fastapi.testclient import TestClient

import pymongo

@pytest.fixture(scope="session", autouse=True)
def clean_db_first():
    mongo_url = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
    sync_client = pymongo.MongoClient(mongo_url)
    db = sync_client.get_default_database("spendwise")
    # Clean up test db BEFORE all tests
    db.users.drop()
    db.accounts.drop()
    db.categories.drop()
    db.transactions.drop()
    db.budgets.drop()
    db.alerts.drop()
    sync_client.close()

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def test_user(client):
    res = client.post("/auth/register", json={
        "email": "testuser@example.com",
        "password": "testpassword",
        "name": "Test User"
    })
    if res.status_code == 400: # Already registered
        res = client.post("/auth/login", json={
            "email": "testuser@example.com",
            "password": "testpassword"
        })
    if res.status_code != 200 and res.status_code != 201:
        try:
            err_msg = res.json()
        except:
            err_msg = res.text
        raise Exception(f"Failed to setup test_user: {err_msg} with Code {res.status_code}")
    return res.json()
