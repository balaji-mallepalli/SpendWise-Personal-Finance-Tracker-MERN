import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import connect_db, close_db
from app.routers import auth, accounts, categories, transactions, budgets, dashboard

load_dotenv()

app = FastAPI(
    title="SpendWise API",
    description="Personal Finance Tracker API",
    version="1.0.0",
)

# CORS
origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in origins_raw.split(",") if o.strip()]

# If "*" is present, we must set allow_credentials=False for browser compatibility
allow_all = "*" in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifecycle events
@app.on_event("startup")
async def startup():
    await connect_db()
    await migrate_category_colors()


async def migrate_category_colors():
    """One-time migration: update colorful category colors to monochrome palette."""
    from app.database import get_db
    db = get_db()
    if db is None:
        return

    color_map = {
        # Original colorful -> new soft gray
        "#ef4444": "#525252",
        "#f97316": "#5e5e5e",
        "#eab308": "#6b6b6b",
        "#22c55e": "#787878",
        "#3b82f6": "#858585",
        "#8b5cf6": "#929292",
        "#ec4899": "#9e9e9e",
        "#10b981": "#ababab",
        "#06b6d4": "#b8b8b8",
        "#6b7280": "#c4c4c4",
        "#6366f1": "#858585",
        # Previous grayscale -> new soft gray
        "#171717": "#525252",
        "#2e2e2e": "#5e5e5e",
        "#454545": "#6b6b6b",
        "#5c5c5c": "#787878",
        "#737373": "#858585",
        "#8a8a8a": "#929292",
        "#a1a1a1": "#9e9e9e",
        "#cfcfcf": "#b8b8b8",
        "#e5e5e5": "#c4c4c4",
    }

    for old_color, new_color in color_map.items():
        result = await db.categories.update_many(
            {"color": old_color},
            {"$set": {"color": new_color}},
        )
        if result.modified_count > 0:
            print(f"  Migrated {result.modified_count} categories: {old_color} -> {new_color}")

@app.on_event("shutdown")
async def shutdown():
    await close_db()

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": "SpendWise API"}
