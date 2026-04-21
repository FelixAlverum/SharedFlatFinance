import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, not_, or_

from app.models.models import User, Transaction, Item, ItemSplit

# Logger für dieses Modul initialisieren
logger = logging.getLogger(__name__)

def get_no_pfand_filter():
    """Hilfsfunktion für den Pfand/Leergut-Filter."""
    return not_(
        or_(
            Item.name.ilike("%pfand%"),
            Item.name.ilike("%leergut%")
        )
    )

def get_total_spend(db: Session) -> list[dict]:
    logger.info("Starte Abfrage: Gesamtausgaben aller Nutzer (ohne Pfand).")
    try:
        result = db.query(
            User.name,
            func.sum(ItemSplit.amount).label("total")
        ).join(ItemSplit, User.email == ItemSplit.user_email)\
         .join(Item, Item.id == ItemSplit.item_id)\
         .filter(get_no_pfand_filter())\
         .group_by(User.name).all()

        logger.debug(f"Erfolgreich berechnet. {len(result)} Nutzer-Datensätze gefunden.")
        return [{"name": row.name, "total_spend": round(row.total or 0, 2)} for row in result]
    
    except Exception as e:
        logger.error("Fehler beim Abrufen der Gesamtausgaben.", exc_info=True)
        raise e

def get_popular_items(db: Session) -> list[dict]:
    logger.info("Starte Abfrage: Beliebteste Artikel (ohne Pfand).")
    try:
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

        logger.debug(f"Erfolgreich geladen. {len(result)} Artikel-Datensätze gefunden.")
        return [{
            "user_email": row.user_email,
            "user_name": row.user_name,
            "name": row.name, 
            "buy_count": row.buy_count, 
            "total_spend": round(row.total_spend or 0, 2)
        } for row in result]
        
    except Exception as e:
        logger.error("Fehler beim Abrufen der beliebtesten Artikel.", exc_info=True)
        raise e

def get_spending_over_time(db: Session, user_email: str, year: int | None = None) -> list[dict]:
    logger.info(f"Starte Abfrage: Ausgaben im Zeitverlauf für User '{user_email}' (Jahr: {year or 'Alle'}).")
    try:
        month_col = func.strftime('%Y-%m', Transaction.date).label("period")
        
        query = db.query(
            month_col,
            func.sum(ItemSplit.amount).label("amount")
        ).join(Item, Transaction.id == Item.transaction_id)\
         .join(ItemSplit, Item.id == ItemSplit.item_id)\
         .filter(ItemSplit.user_email == user_email)\
         .filter(get_no_pfand_filter())

        if year:
            query = query.filter(func.strftime('%Y', Transaction.date) == str(year))

        result = query.group_by(month_col).order_by(month_col).all()

        logger.debug(f"Zeitverlauf für '{user_email}' erfolgreich geladen. {len(result)} Monate gefunden.")
        return [{"period": row.period, "amount": round(row.amount or 0, 2)} for row in result]
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Zeitverlaufs für User '{user_email}'.", exc_info=True)
        raise e

def get_category_spend(db: Session, user_email: str) -> list[dict]:
    logger.info(f"Starte Abfrage: Ausgaben nach Kategorie für User '{user_email}'.")
    try:
        result = db.query(
            func.coalesce(Item.category, 'Unkategorisiert').label("category"),
            func.sum(ItemSplit.amount).label("amount")
        ).join(ItemSplit, Item.id == ItemSplit.item_id)\
         .filter(ItemSplit.user_email == user_email)\
         .filter(get_no_pfand_filter())\
         .group_by("category")\
         .order_by(desc("amount")).all()

        logger.debug(f"Kategorien für '{user_email}' erfolgreich geladen. {len(result)} Kategorien gefunden.")
        return [{"category": row.category, "amount": round(row.amount or 0, 2)} for row in result]
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Kategorie-Ausgaben für User '{user_email}'.", exc_info=True)
        raise e