import logging
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.models import Transaction, Item, ItemSplit, User
from app.schemas.transaction import TransactionCreate

# 1. Logger initialisieren
logger = logging.getLogger(__name__)

def _validate_users_exist(db: Session, tx_in: TransactionCreate):
    """
    Hilfsfunktion: Holt ALLE benötigten E-Mails (Bezahler + Splits) 
    und prüft sie mit nur EINER einzigen Datenbankabfrage. (Performance-Boost)
    """
    needed_emails = {tx_in.payer_email}
    for item in tx_in.items:
        for split in item.splits:
            needed_emails.add(split.user_email)
            
    existing_users = db.query(User.email).filter(User.email.in_(needed_emails)).all()
    existing_emails = {u[0] for u in existing_users}
    
    missing_users = needed_emails - existing_emails
    if missing_users:
        logger.warning(f"Validierung fehlgeschlagen. Unbekannte Nutzer: {missing_users}")
        raise ValueError(f"Folgende Nutzer existieren nicht im System: {', '.join(missing_users)}")


def create_transaction(db: Session, tx_in: TransactionCreate) -> Transaction:
    logger.info(f"Erstelle neue Transaktion: '{tx_in.title}' bezahlt von {tx_in.payer_email}")
    
    try:
        # 1. Alle Nutzer vorab mit einer Query validieren
        _validate_users_exist(db, tx_in)

        # 2. Den Haupt-Bon erstellen
        db_tx = Transaction(
            title=tx_in.title,
            date=tx_in.date or datetime.utcnow(),
            payer_email=tx_in.payer_email
        )
        db.add(db_tx)
        db.flush()

        # 3. Items und Splits einfügen
        for item_in in tx_in.items:
            db_item = Item(
                transaction_id=db_tx.id,
                name=item_in.name,
                quantity=item_in.quantity,
                unit_price=item_in.unit_price,
                total_price=item_in.total_price,
                category=item_in.category
            )
            db.add(db_item)
            db.flush() 

            for split_in in item_in.splits:
                db_split = ItemSplit(
                    item_id=db_item.id,
                    user_email=split_in.user_email,
                    amount=split_in.amount
                )
                db.add(db_split)

        db.commit()
        db.refresh(db_tx)
        logger.info(f"Transaktion erfolgreich erstellt (ID: {db_tx.id}) mit {len(tx_in.items)} Items.")
        return db_tx

    except Exception as e:
        db.rollback() # WICHTIG: DB-Status zurücksetzen bei Fehler!
        logger.error(f"Fehler beim Erstellen der Transaktion: {str(e)}", exc_info=True)
        raise e


def get_transactions(db: Session, skip: int = 0, limit: int = 15) -> list[Transaction]:
    logger.debug(f"Lade Transaktionen (Skip: {skip}, Limit: {limit})")
    return db.query(Transaction)\
        .order_by(Transaction.date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_transaction(db: Session, tx_id: int) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.id == tx_id).first()


def update_transaction(db: Session, tx_id: int, tx_in: TransactionCreate) -> Transaction:
    logger.info(f"Starte Update für Transaktion ID: {tx_id}")
    
    db_tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not db_tx:
        logger.error(f"Update abgebrochen: Transaktion ID {tx_id} nicht gefunden.")
        raise ValueError(f"Transaktion mit ID {tx_id} nicht gefunden.")

    try:
        # 1. Nutzer validieren (Performance-Boost)
        _validate_users_exist(db, tx_in)

        # 2. Kopfdaten der Transaktion aktualisieren
        db_tx.title = tx_in.title
        db_tx.date = tx_in.date or db_tx.date
        db_tx.payer_email = tx_in.payer_email
        
        item_ids = [item.id for item in db_tx.items]
        if item_ids:
            logger.debug(f"Lösche alte Splits und Items für Transaktion {tx_id}")
            db.query(ItemSplit).filter(ItemSplit.item_id.in_(item_ids)).delete(synchronize_session='fetch')
            db.query(Item).filter(Item.transaction_id == tx_id).delete(synchronize_session='fetch')
            db.flush()

        # 4. NEUE ITEMS & SPLITS EINFÜGEN
        logger.debug(f"Füge {len(tx_in.items)} neue Items ein...")
        for item_in in tx_in.items:
            new_item = Item(
                transaction_id=db_tx.id,
                name=item_in.name,
                quantity=item_in.quantity,
                unit_price=item_in.unit_price,
                total_price=item_in.total_price,
                category=item_in.category
            )
            db.add(new_item)
            db.flush()

            for split_in in item_in.splits:
                new_split = ItemSplit(
                    item_id=new_item.id,
                    user_email=split_in.user_email,
                    amount=split_in.amount
                )
                db.add(new_split)

        db.commit()
        db.refresh(db_tx)
        logger.info(f"Update für Transaktion ID {tx_id} erfolgreich abgeschlossen.")
        return db_tx

    except Exception as e:
        db.rollback()
        logger.error(f"Kritischer Fehler beim Update der Transaktion {tx_id}: {str(e)}", exc_info=True)
        raise e


def delete_transaction(db: Session, tx_id: int) -> bool:
    logger.info(f"Versuche Transaktion ID {tx_id} zu löschen.")
    db_tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    
    if not db_tx:
        logger.warning(f"Löschen fehlgeschlagen: Transaktion ID {tx_id} existiert nicht.")
        return False
        
    try:
        db.delete(db_tx) 
        db.commit()
        logger.info(f"Transaktion ID {tx_id} erfolgreich gelöscht.")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Fehler beim Löschen der Transaktion {tx_id}: {str(e)}", exc_info=True)
        raise e