from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from app.models.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetStatus
from app.auth.deps import get_current_user
from app.database import get_db
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()


def budget_doc_to_response(doc: dict) -> BudgetResponse:
    return BudgetResponse(
        id=str(doc["_id"]),
        user_id=str(doc["user_id"]),
        category_id=str(doc["category_id"]),
        month=doc["month"],
        year=doc["year"],
        limit_amount=round(doc["limit_amount"], 2),
    )


@router.get("/status", response_model=List[BudgetStatus])
async def get_budget_status(
    current_user: dict = Depends(get_current_user),
    month: int = Query(default=None),
    year: int = Query(default=None),
):
    db = get_db()
    now = datetime.now(timezone.utc)
    m = month or now.month
    y = year or now.year

    budgets = await db.budgets.find({
        "user_id": ObjectId(current_user["id"]),
        "month": m,
        "year": y,
    }).to_list(length=100)

    results = []
    for budget in budgets:
        cat = await db.categories.find_one({"_id": budget["category_id"]})
        cat_name = cat["name"] if cat else "Unknown"
        cat_color = cat.get("color", "#737373") if cat else "#737373"
        cat_icon = cat.get("icon", "📁") if cat else "📁"

        # Calculate spent for this category this month
        start = datetime(y, m, 1, tzinfo=timezone.utc)
        if m < 12:
            end = datetime(y, m + 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(y + 1, 1, 1, tzinfo=timezone.utc)

        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(current_user["id"]),
                    "category_id": budget["category_id"],
                    "type": "expense",
                    "date": {"$gte": start, "$lt": end},
                }
            },
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]
        agg_result = await db.transactions.aggregate(pipeline).to_list(length=1)
        spent = round(agg_result[0]["total"], 2) if agg_result else 0.0
        limit_amt = round(budget["limit_amount"], 2)
        pct = round((spent / limit_amt) * 100, 1) if limit_amt > 0 else 0.0

        results.append(BudgetStatus(
            id=str(budget["_id"]),
            category_id=str(budget["category_id"]),
            category_name=cat_name,
            category_color=cat_color,
            category_icon=cat_icon,
            month=m,
            year=y,
            limit_amount=limit_amt,
            spent_amount=spent,
            percentage=pct,
            exceeded=pct >= 100,
        ))

    return results


@router.get("/", response_model=List[BudgetResponse])
async def list_budgets(
    current_user: dict = Depends(get_current_user),
    month: int = Query(default=None),
    year: int = Query(default=None),
):
    db = get_db()
    now = datetime.now(timezone.utc)
    query = {"user_id": ObjectId(current_user["id"])}
    if month:
        query["month"] = month
    if year:
        query["year"] = year
    if not month and not year:
        query["month"] = now.month
        query["year"] = now.year
    budgets = await db.budgets.find(query).to_list(length=100)
    return [budget_doc_to_response(b) for b in budgets]


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: BudgetCreate, current_user: dict = Depends(get_current_user)
):
    db = get_db()
    # Check for duplicate budget
    existing = await db.budgets.find_one({
        "user_id": ObjectId(current_user["id"]),
        "category_id": ObjectId(data.category_id),
        "month": data.month,
        "year": data.year,
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Budget already exists for this category and month",
        )
    doc = {
        "user_id": ObjectId(current_user["id"]),
        "category_id": ObjectId(data.category_id),
        "month": data.month,
        "year": data.year,
        "limit_amount": round(data.limit_amount, 2),
    }
    result = await db.budgets.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Create default alert
    alert_doc = {
        "user_id": ObjectId(current_user["id"]),
        "budget_id": result.inserted_id,
        "threshold_pct": 90,
        "triggered_at": None,
    }
    await db.alerts.insert_one(alert_doc)

    return budget_doc_to_response(doc)


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    data: BudgetUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    budget = await db.budgets.find_one(
        {"_id": ObjectId(budget_id), "user_id": ObjectId(current_user["id"])}
    )
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    update_data = {}
    for k, v in data.model_dump().items():
        if v is not None:
            if k == "category_id":
                update_data[k] = ObjectId(v)
            elif k == "limit_amount":
                update_data[k] = round(v, 2)
            else:
                update_data[k] = v
    if update_data:
        await db.budgets.update_one(
            {"_id": ObjectId(budget_id)}, {"$set": update_data}
        )
    updated = await db.budgets.find_one({"_id": ObjectId(budget_id)})
    return budget_doc_to_response(updated)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str, current_user: dict = Depends(get_current_user)
):
    db = get_db()
    result = await db.budgets.delete_one(
        {"_id": ObjectId(budget_id), "user_id": ObjectId(current_user["id"])}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Budget not found")
    # Also delete associated alerts
    await db.alerts.delete_many({"budget_id": ObjectId(budget_id)})
