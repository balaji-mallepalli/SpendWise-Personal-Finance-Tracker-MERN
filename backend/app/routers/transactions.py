from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from fastapi.responses import StreamingResponse
from app.models.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.auth.deps import get_current_user
from app.database import get_db
from bson import ObjectId
from datetime import datetime, timezone
import csv
import io

router = APIRouter()


def txn_doc_to_response(doc: dict) -> TransactionResponse:
    return TransactionResponse(
        id=str(doc["_id"]),
        user_id=str(doc["user_id"]),
        account_id=str(doc["account_id"]),
        category_id=str(doc["category_id"]),
        amount=round(doc["amount"], 2),
        type=doc["type"],
        description=doc.get("description", ""),
        date=doc["date"].isoformat() if isinstance(doc["date"], datetime) else str(doc["date"]),
        created_at=doc["created_at"].isoformat() if isinstance(doc["created_at"], datetime) else str(doc["created_at"]),
    )


async def _check_and_trigger_alerts(db, user_id: str, category_id: str, txn_date: datetime):
    """Check if any budget alert should be triggered after a new expense."""
    month = txn_date.month
    year = txn_date.year
    budget = await db.budgets.find_one({
        "user_id": ObjectId(user_id),
        "category_id": ObjectId(category_id),
        "month": month,
        "year": year,
    })
    if not budget:
        return

    # Calculate total spent this month for this category
    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(user_id),
                "category_id": ObjectId(category_id),
                "type": "expense",
                "date": {
                    "$gte": datetime(year, month, 1, tzinfo=timezone.utc),
                    "$lt": datetime(year, month + 1 if month < 12 else 1, 1, tzinfo=timezone.utc) if month < 12 else datetime(year + 1, 1, 1, tzinfo=timezone.utc),
                },
            }
        },
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]
    result = await db.transactions.aggregate(pipeline).to_list(length=1)
    spent = result[0]["total"] if result else 0

    # Check alerts for this budget
    alerts = await db.alerts.find({"budget_id": budget["_id"]}).to_list(length=10)
    for alert in alerts:
        threshold = alert.get("threshold_pct", 90)
        if spent >= (budget["limit_amount"] * threshold / 100):
            if not alert.get("triggered_at"):
                await db.alerts.update_one(
                    {"_id": alert["_id"]},
                    {"$set": {"triggered_at": datetime.now(timezone.utc)}},
                )

    # Also auto-create a default alert if none exists
    if not alerts:
        alert_doc = {
            "user_id": ObjectId(user_id),
            "budget_id": budget["_id"],
            "threshold_pct": 90,
            "triggered_at": None,
        }
        if spent >= (budget["limit_amount"] * 0.9):
            alert_doc["triggered_at"] = datetime.now(timezone.utc)
        await db.alerts.insert_one(alert_doc)


@router.get("/export")
async def export_transactions(
    current_user: dict = Depends(get_current_user),
    start_date: str = Query(default=None),
    end_date: str = Query(default=None),
):
    db = get_db()
    query = {"user_id": ObjectId(current_user["id"])}
    if start_date:
        query["date"] = {"$gte": datetime.fromisoformat(start_date)}
    if end_date:
        query.setdefault("date", {})
        query["date"]["$lte"] = datetime.fromisoformat(end_date)

    cursor = db.transactions.find(query).sort("date", -1)
    transactions = await cursor.to_list(length=5000)

    # Look up category names
    cat_ids = list(set(t["category_id"] for t in transactions))
    categories = {}
    if cat_ids:
        cat_docs = await db.categories.find({"_id": {"$in": cat_ids}}).to_list(length=200)
        categories = {str(c["_id"]): c["name"] for c in cat_docs}

    # Look up account names
    acc_ids = list(set(t["account_id"] for t in transactions))
    accounts = {}
    if acc_ids:
        acc_docs = await db.accounts.find({"_id": {"$in": acc_ids}}).to_list(length=100)
        accounts = {str(a["_id"]): a["name"] for a in acc_docs}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Type", "Category", "Account", "Amount", "Description"])
    for t in transactions:
        writer.writerow([
            t["date"].strftime("%Y-%m-%d") if isinstance(t["date"], datetime) else t["date"],
            t["type"],
            categories.get(str(t["category_id"]), "Unknown"),
            accounts.get(str(t["account_id"]), "Unknown"),
            round(t["amount"], 2),
            t.get("description", ""),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    current_user: dict = Depends(get_current_user),
    start_date: str = Query(default=None),
    end_date: str = Query(default=None),
    category_id: str = Query(default=None),
    type: str = Query(default=None),
    account_id: str = Query(default=None),
):
    db = get_db()
    query = {"user_id": ObjectId(current_user["id"])}
    if start_date:
        query["date"] = {"$gte": datetime.fromisoformat(start_date)}
    if end_date:
        query.setdefault("date", {})
        query["date"]["$lte"] = datetime.fromisoformat(end_date)
    if category_id:
        query["category_id"] = ObjectId(category_id)
    if type:
        query["type"] = type
    if account_id:
        query["account_id"] = ObjectId(account_id)

    cursor = db.transactions.find(query).sort("date", -1)
    transactions = await cursor.to_list(length=500)
    return [txn_doc_to_response(t) for t in transactions]


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate, current_user: dict = Depends(get_current_user)
):
    db = get_db()
    # Verify account belongs to user
    account = await db.accounts.find_one(
        {"_id": ObjectId(data.account_id), "user_id": ObjectId(current_user["id"])}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    doc = {
        "user_id": ObjectId(current_user["id"]),
        "account_id": ObjectId(data.account_id),
        "category_id": ObjectId(data.category_id),
        "amount": round(data.amount, 2),
        "type": data.type,
        "description": data.description,
        "date": data.date,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.transactions.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Update account balance
    balance_change = doc["amount"] if doc["type"] == "income" else -doc["amount"]
    await db.accounts.update_one(
        {"_id": ObjectId(data.account_id)},
        {"$inc": {"balance": round(balance_change, 2)}},
    )

    # Check budget alerts for expenses
    if doc["type"] == "expense":
        await _check_and_trigger_alerts(db, current_user["id"], data.category_id, data.date)

    return txn_doc_to_response(doc)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    txn = await db.transactions.find_one(
        {"_id": ObjectId(transaction_id), "user_id": ObjectId(current_user["id"])}
    )
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = {}
    raw = data.model_dump()
    for k, v in raw.items():
        if v is not None:
            if k in ("account_id", "category_id"):
                update_data[k] = ObjectId(v)
            elif k == "amount":
                update_data[k] = round(v, 2)
            else:
                update_data[k] = v

    # Handle balance recalculation
    if "amount" in update_data or "type" in update_data:
        old_change = txn["amount"] if txn["type"] == "income" else -txn["amount"]
        new_amount = update_data.get("amount", txn["amount"])
        new_type = update_data.get("type", txn["type"])
        new_change = new_amount if new_type == "income" else -new_amount
        diff = new_change - old_change
        target_account = update_data.get("account_id", txn["account_id"])
        await db.accounts.update_one(
            {"_id": target_account},
            {"$inc": {"balance": round(diff, 2)}},
        )

    if update_data:
        await db.transactions.update_one(
            {"_id": ObjectId(transaction_id)}, {"$set": update_data}
        )
    updated = await db.transactions.find_one({"_id": ObjectId(transaction_id)})
    return txn_doc_to_response(updated)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str, current_user: dict = Depends(get_current_user)
):
    db = get_db()
    txn = await db.transactions.find_one(
        {"_id": ObjectId(transaction_id), "user_id": ObjectId(current_user["id"])}
    )
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Reverse balance change
    balance_change = txn["amount"] if txn["type"] == "income" else -txn["amount"]
    await db.accounts.update_one(
        {"_id": txn["account_id"]},
        {"$inc": {"balance": round(-balance_change, 2)}},
    )
    await db.transactions.delete_one({"_id": ObjectId(transaction_id)})
