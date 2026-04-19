from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.auth.jwt_handler import hash_password, verify_password, create_access_token
from app.auth.deps import get_current_user
from app.database import get_db
from datetime import datetime, timezone

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    db = get_db()
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user_doc = {
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "name": user_data.name,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_access_token({"sub": user_id})

    # Seed default categories for new user
    default_categories = [
        {"user_id": None, "name": "Food & Dining", "icon": "🍔", "color": "#525252"},
        {"user_id": None, "name": "Transportation", "icon": "🚗", "color": "#5e5e5e"},
        {"user_id": None, "name": "Shopping", "icon": "🛍️", "color": "#6b6b6b"},
        {"user_id": None, "name": "Entertainment", "icon": "🎬", "color": "#787878"},
        {"user_id": None, "name": "Bills & Utilities", "icon": "💡", "color": "#858585"},
        {"user_id": None, "name": "Health", "icon": "🏥", "color": "#929292"},
        {"user_id": None, "name": "Education", "icon": "📚", "color": "#9e9e9e"},
        {"user_id": None, "name": "Salary", "icon": "💰", "color": "#ababab"},
        {"user_id": None, "name": "Freelance", "icon": "💻", "color": "#b8b8b8"},
        {"user_id": None, "name": "Other", "icon": "📦", "color": "#c4c4c4"},
    ]
    # Only seed if no system categories exist yet
    count = await db.categories.count_documents({"user_id": None})
    if count == 0:
        await db.categories.insert_many(default_categories)

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=user_doc["email"],
            name=user_doc["name"],
            created_at=user_doc["created_at"],
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    user_id = str(user["_id"])
    token = create_access_token({"sub": user_id})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=user["email"],
            name=user["name"],
            created_at=user["created_at"],
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        created_at=current_user["created_at"],
    )
