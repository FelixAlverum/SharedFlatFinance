from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional

from app.db.session import get_db
from app.models.models import User, Transaction, Item, ItemSplit
from app.api.deps import get_current_user
from app.schemas import stats as schemas

router = APIRouter()

# --- 1. GESAMTE AUSGABEN PRO USER (Die echten Kosten) ---
@router.get("/total-spend", response_model=list[schemas.UserTotalSpend])
def get_total_spend(db: Session = Depends(get_db)):
    """Berechnet, wie viel jeder User insgesamt *verbraucht* hat (Summe seiner Splits)"""
    
    result = db.query(
        User.name,
        func.sum(ItemSplit.amount).label("total")
    ).join(ItemSplit, User.email == ItemSplit.user_email)\
     .group_by(User.name).all()

    return [{"name": row.name, "total_spend": round(row.total or 0, 2)} for row in result]


# --- 2. BELIEBTESTE ITEMS EINES USERS ---
@router.get("/popular-items", response_model=list[schemas.PopularItem])
def get_popular_items(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Zeigt die am häufigsten gekauften Produkte des eingeloggten Users (ohne Pfand)"""
    
    result = db.query(
        Item.name,
        func.count(Item.id).label("buy_count"),
        func.sum(ItemSplit.amount).label("total_spend")
    ).join(ItemSplit, Item.id == ItemSplit.item_id)\
     .filter(ItemSplit.user_email == current_user.email)\
     .filter(ItemSplit.amount > 0) \
     .group_by(Item.name)\
     .order_by(desc("buy_count"))\
     .limit(limit).all()

    return [{
        "name": row.name, 
        "buy_count": row.buy_count, 
        "total_spend": round(row.total_spend or 0, 2)
    } for row in result]


# --- 3. ZEITLICHER VERLAUF (Ausgaben pro Monat) ---
@router.get("/spending-over-time", response_model=list[schemas.TimeSeriesData])
def get_spending_over_time(
    year: Optional[int] = None,  # <-- NEU: Optionaler Query-Parameter
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggregiert die Ausgaben des eingeloggten Users nach Jahr-Monat (z.B. 2023-10).
    Kann durch den Query-Parameter ?year=YYYY auf ein bestimmtes Jahr gefiltert werden.
    """
    
    # SQLite spezifisch: strftime extrahiert das Jahr und den Monat aus dem DateTime
    month_col = func.strftime('%Y-%m', Transaction.date).label("period")
    
    # Basis-Abfrage aufbauen (noch nicht ausführen!)
    query = db.query(
        month_col,
        func.sum(ItemSplit.amount).label("amount")
    ).join(Item, Transaction.id == Item.transaction_id)\
     .join(ItemSplit, Item.id == ItemSplit.item_id)\
     .filter(ItemSplit.user_email == current_user.email)

    if year:
        query = query.filter(func.strftime('%Y', Transaction.date) == str(year))

    result = query.group_by(month_col).order_by(month_col).all()

    return [{"period": row.period, "amount": round(row.amount or 0, 2)} for row in result]


# --- 4. WEITERE STATISTIK: AUSGABEN NACH KATEGORIE ---
@router.get("/category-spend", response_model=list[schemas.CategorySpend])
def get_category_spend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """WG-Insights: Wofür gibt der User sein Geld aus? (Lebensmittel vs. Haushalt)"""
    
    result = db.query(
        # coalesce ersetzt NULL-Werte durch "Unkategorisiert"
        func.coalesce(Item.category, 'Unkategorisiert').label("category"),
        func.sum(ItemSplit.amount).label("amount")
    ).join(ItemSplit, Item.id == ItemSplit.item_id)\
     .filter(ItemSplit.user_email == current_user.email)\
     .filter(ItemSplit.amount > 0)\
     .group_by("category")\
     .order_by(desc("amount")).all()

    return [{"category": row.category, "amount": round(row.amount or 0, 2)} for row in result]