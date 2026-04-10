from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.session import get_db
from app.models.models import User, Transaction, Item, ItemSplit
from app.schemas.balance import UserBalance
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[UserBalance])
def get_balances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Summe aller Ausgaben pro Payer berechnen
    # Wir joinen Transaction -> Item, um den total_price zu summieren
    paid_query = db.query(
        Transaction.payer_email,
        func.sum(Item.total_price).label("total_paid")
    ).join(Item).group_by(Transaction.payer_email).subquery()

    # 2. Summe aller Schulden pro User aus den Splits berechnen
    debt_query = db.query(
        ItemSplit.user_email,
        func.sum(ItemSplit.amount).label("total_debt")
    ).group_by(ItemSplit.user_email).subquery()

    # 3. Alle User abrufen und die Werte verrechnen
    # Wir nutzen coalesce(..., 0), damit User ohne Transaktionen nicht 'None' sind
    users_with_balances = db.query(
        User.email,
        User.name,
        (func.coalesce(paid_query.c.total_paid, 0) - 
         func.coalesce(debt_query.c.total_debt, 0)).label("balance")
    ).outerjoin(paid_query, User.email == paid_query.c.payer_email)\
     .outerjoin(debt_query, User.email == debt_query.c.user_email)\
     .all()

    # Formatierung für die Response
    return [
        UserBalance(
            email=u.email,
            name=u.name,
            amount=round(u.balance, 2)
        ) for u in users_with_balances
    ]