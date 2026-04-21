import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import User, Transaction, Item, ItemSplit
from app.schemas.balance import UserBalance

logger = logging.getLogger(__name__)

def calculate_user_balances(db: Session) -> List[UserBalance]:
    """ Berechnet Kontostände aller User und gibt eine Liste von UserBalance zurück. """
    logger.info("Starte Berechnung der User-Kontostände (Balances).")

    try:
        # 1. Summe aller Ausgaben pro Payer (Transaction -> Item join) berechnen
        paid_query = db.query(
            Transaction.payer_email,
            func.sum(Item.total_price).label("total_paid")
        ).join(Item).group_by(Transaction.payer_email).subquery()

        # 2. Summe aller Schulden pro User aus Splits berechnen
        debt_query = db.query(
            ItemSplit.user_email,
            func.sum(ItemSplit.amount).label("total_debt")
        ).group_by(ItemSplit.user_email).subquery()

        # 3. User abrufen und Werte mit coalesce (gegen NULL) verrechnen
        users_with_balances = db.query(
            User.email,
            User.name,
            (func.coalesce(paid_query.c.total_paid, 0) - 
             func.coalesce(debt_query.c.total_debt, 0)).label("balance")
        ).outerjoin(paid_query, User.email == paid_query.c.payer_email)\
         .outerjoin(debt_query, User.email == debt_query.c.user_email)\
         .all()

        logger.debug(f"Rohdaten für {len(users_with_balances)} User aus Datenbank abgerufen.")

        # Formatierung als Liste von Pydantic Models
        balances = [
            UserBalance(
                email=u.email,
                name=u.name,
                amount=round(u.balance, 2)
            ) for u in users_with_balances
        ]

        logger.info("Berechnung der Kontostände erfolgreich abgeschlossen.")
        return balances

    except Exception as e:
        logger.error("Fehler bei der Berechnung der Kontostände.", exc_info=True)
        raise e