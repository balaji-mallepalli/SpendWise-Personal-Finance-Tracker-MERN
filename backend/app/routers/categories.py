from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.auth.deps import get_current_user
from app.database import get_db
from bson import ObjectId

router = APIRouter()


def category_doc_to_response(doc: dict) -> CategoryResponse:
    return CategoryResponse(
        id=str(doc["_id"]),
        user_id=str(doc["user_id"]) if doc.get("user_id") else None,
        name=doc["name"],
        icon=doc.get("icon", "📁"),
        color=doc.get("color", "#737373"),
    )


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(current_user: dict = Depends(get_current_user)):
    db = get_db()
    # Return system categories (user_id=None) + user's custom categories
    cursor = db.categories.find(
        {"$or": [{"user_id": None}, {"user_id": ObjectId(current_user["id"])}]}
    )
    categories = await cursor.to_list(length=200)
    return [category_doc_to_response(c) for c in categories]


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate, current_user: dict = Depends(get_current_user)
):
    db = get_db()
    doc = {
        "user_id": ObjectId(current_user["id"]),
        "name": data.name,
        "icon": data.icon,
        "color": data.color,
    }
    result = await db.categories.insert_one(doc)
    doc["_id"] = result.inserted_id
    return category_doc_to_response(doc)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    data: CategoryUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    category = await db.categories.find_one({"_id": ObjectId(category_id)})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    # Can only edit own custom categories
    if category.get("user_id") and str(category["user_id"]) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cannot edit this category")
    if not category.get("user_id"):
        raise HTTPException(status_code=403, detail="Cannot edit system categories")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if update_data:
        await db.categories.update_one(
            {"_id": ObjectId(category_id)}, {"$set": update_data}
        )
    updated = await db.categories.find_one({"_id": ObjectId(category_id)})
    return category_doc_to_response(updated)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str, current_user: dict = Depends(get_current_user)
):
    db = get_db()
    category = await db.categories.find_one({"_id": ObjectId(category_id)})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if not category.get("user_id"):
        raise HTTPException(status_code=403, detail="Cannot delete system categories")
    if str(category["user_id"]) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cannot delete this category")
    await db.categories.delete_one({"_id": ObjectId(category_id)})
