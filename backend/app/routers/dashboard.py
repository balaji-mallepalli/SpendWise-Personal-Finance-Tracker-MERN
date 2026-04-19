from fastapi import APIRouter, Depends, Query
from app.auth.deps import get_current_user
from app.database import get_db
from bson import ObjectId
from datetime import datetime, timezone, timedelta

router = APIRouter()


@router.get("/summary")
async def dashboard_summary(
    current_user: dict = Depends(get_current_user),
    month: int = Query(default=None),
    year: int = Query(default=None),
):
    db = get_db()
    now = datetime.now(timezone.utc)
    m = month or now.month
    y = year or now.year

    start = datetime(y, m, 1, tzinfo=timezone.utc)
    if m < 12:
        end = datetime(y, m + 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(y + 1, 1, 1, tzinfo=timezone.utc)

    user_oid = ObjectId(current_user["id"])

    # Income total
    income_pipeline = [
        {"$match": {"user_id": user_oid, "type": "income", "date": {"$gte": start, "$lt": end}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]
    income_result = await db.transactions.aggregate(income_pipeline).to_list(length=1)
    total_income = round(income_result[0]["total"], 2) if income_result else 0.0

    # Expense total
    expense_pipeline = [
        {"$match": {"user_id": user_oid, "type": "expense", "date": {"$gte": start, "$lt": end}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]
    expense_result = await db.transactions.aggregate(expense_pipeline).to_list(length=1)
    total_expense = round(expense_result[0]["total"], 2) if expense_result else 0.0

    # Triggered alerts count
    alerts = await db.alerts.find({
        "user_id": user_oid,
        "triggered_at": {"$ne": None},
    }).to_list(length=100)

    return {
        "month": m,
        "year": y,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": round(total_income - total_expense, 2),
        "active_alerts": len(alerts),
    }


@router.get("/by-category")
async def spending_by_category(
    current_user: dict = Depends(get_current_user),
    month: int = Query(default=None),
    year: int = Query(default=None),
):
    db = get_db()
    now = datetime.now(timezone.utc)
    m = month or now.month
    y = year or now.year

    start = datetime(y, m, 1, tzinfo=timezone.utc)
    if m < 12:
        end = datetime(y, m + 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(y + 1, 1, 1, tzinfo=timezone.utc)

    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(current_user["id"]),
                "type": "expense",
                "date": {"$gte": start, "$lt": end},
            }
        },
        {"$group": {"_id": "$category_id", "total": {"$sum": "$amount"}}},
        {"$sort": {"total": -1}},
    ]
    results = await db.transactions.aggregate(pipeline).to_list(length=50)

    # Look up category info
    categories = []
    for r in results:
        cat = await db.categories.find_one({"_id": r["_id"]})
        categories.append({
            "category_id": str(r["_id"]),
            "category_name": cat["name"] if cat else "Unknown",
            "category_color": cat.get("color", "#737373") if cat else "#737373",
            "category_icon": cat.get("icon", "📁") if cat else "📁",
            "amount": round(r["total"], 2),
        })

    return categories


@router.get("/over-time")
async def spending_over_time(
    current_user: dict = Depends(get_current_user),
    days: int = Query(default=30),
):
    db = get_db()
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)

    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(current_user["id"]),
                "type": "expense",
                "date": {"$gte": start},
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$date"}
                },
                "total": {"$sum": "$amount"},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    results = await db.transactions.aggregate(pipeline).to_list(length=60)

    return [
        {"date": r["_id"], "amount": round(r["total"], 2)}
        for r in results
    ]
