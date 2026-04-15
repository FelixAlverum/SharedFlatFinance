from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, not_, or_  # <-- NEU: not_ und or_ importieren

from app.db.session import get_db
from app.models.models import User, Transaction, Item, ItemSplit
from app.api.deps import get_current_user
from app.schemas import stats as schemas

router = APIRouter()

# --- HILFS-FILTER ---
def get_no_pfand_filter():
    return not_(
        or_(
            Item.name.ilike("%pfand%"),
            Item.name.ilike("%leergut%")
        )
    )

# --- 1. GESAMTE AUSGABEN PRO USER ---
@router.get("/total-spend", response_model=list[schemas.UserTotalSpend])
def get_total_spend(db: Session = Depends(get_db)):
    result = db.query(
        User.name,
        func.sum(ItemSplit.amount).label("total")
    ).join(ItemSplit, User.email == ItemSplit.user_email)\
     .join(Item, Item.id == ItemSplit.item_id)\
     .filter(get_no_pfand_filter())\
     .group_by(User.name).all()

    return [{"name": row.name, "total_spend": round(row.total or 0, 2)} for row in result]


# --- 2. BELIEBTESTE ITEMS EINES USERS ---
@router.get("/popular-items")
def get_popular_items(db: Session = Depends(get_db)):
    """Zeigt alle Produkte an, aufgeschlüsselt nach JEDEM User (ohne Pfand!)"""
    
    result = db.query(
        User.email.label("user_email"),
        User.name.label("user_name"),
        Item.name,
        func.count(Item.id).label("buy_count"),
        func.sum(ItemSplit.amount).label("total_spend")
    ).join(ItemSplit, Item.id == ItemSplit.item_id)\
     .join(User, User.email == ItemSplit.user_email)\
     .filter(ItemSplit.amount > 0)\
     .filter(get_no_pfand_filter()) \
     .group_by(User.email, User.name, Item.name)\
     .order_by(desc("buy_count")).all()

    return [{
        "user_email": row.user_email,
        "user_name": row.user_name,
        "name": row.name, 
        "buy_count": row.buy_count, 
        "total_spend": round(row.total_spend or 0, 2)
    } for row in result]


# --- 3. ZEITLICHER VERLAUF ---
@router.get("/spending-over-time", response_model=list[schemas.TimeSeriesData])
def get_spending_over_time(
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    month_col = func.strftime('%Y-%m', Transaction.date).label("period")
    
    query = db.query(
        month_col,
        func.sum(ItemSplit.amount).label("amount")
    ).join(Item, Transaction.id == Item.transaction_id)\
     .join(ItemSplit, Item.id == ItemSplit.item_id)\
     .filter(ItemSplit.user_email == current_user.email)\
     .filter(get_no_pfand_filter())

    if year:
        query = query.filter(func.strftime('%Y', Transaction.date) == str(year))

    result = query.group_by(month_col).order_by(month_col).all()

    return [{"period": row.period, "amount": round(row.amount or 0, 2)} for row in result]


# --- 4. KATEGORIEN ---
@router.get("/category-spend", response_model=list[schemas.CategorySpend])
def get_category_spend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(
        func.coalesce(Item.category, 'Unkategorisiert').label("category"),
        func.sum(ItemSplit.amount).label("amount")
    ).join(ItemSplit, Item.id == ItemSplit.item_id)\
     .filter(ItemSplit.user_email == current_user.email)\
     .filter(get_no_pfand_filter())\
     .group_by("category")\
     .order_by(desc("amount")).all()

    return [{"category": row.category, "amount": round(row.amount or 0, 2)} for row in result]