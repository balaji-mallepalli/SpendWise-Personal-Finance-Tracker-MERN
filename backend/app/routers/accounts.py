from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.account import AccountCreate, AccountUpdate, AccountResponse
from app.auth.deps import get_current_user
from app.database import get_db
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()


def account_doc_to_response(doc: dict) -> AccountResponse:
    return AccountResponse(
        id=str(doc["_id"]),
        user_id=str(doc["user_id"]),
        name=doc["name"],
        type=doc["type"],
        balance=round(doc["balance"], 2),
        created_at=doc["created_at"].isoformat(),
    )


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.accounts.find({"user_id": ObjectId(current_user["id"])})
    accounts = await cursor.to_list(length=100)
    return [account_doc_to_response(a) for a in accounts]


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate, current_user: dict = Depends(get_current_user)
):
    db = get_db()
    doc = {
        "user_id": ObjectId(current_user["id"]),
        "name": data.name,
        "type": data.type,
        "balance": round(data.balance, 2),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.accounts.insert_one(doc)
    doc["_id"] = result.inserted_id
    return account_doc_to_response(doc)


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    data: AccountUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    account = await db.accounts.find_one(
        {"_id": ObjectId(account_id), "user_id": ObjectId(current_user["id"])}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if "balance" in update_data:
        update_data["balance"] = round(update_data["balance"], 2)
    if update_data:
        await db.accounts.update_one(
            {"_id": ObjectId(account_id)}, {"$set": update_data}
        )
    updated = await db.accounts.find_one({"_id": ObjectId(account_id)})
    return account_doc_to_response(updated)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str, current_user: dict = Depends(get_current_user)
):
    db = get_db()
    result = await db.accounts.delete_one(
        {"_id": ObjectId(account_id), "user_id": ObjectId(current_user["id"])}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
