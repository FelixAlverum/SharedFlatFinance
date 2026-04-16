from sqlalchemy.orm import Session
from datetime import datetime
from app.models.models import Transaction, Item, ItemSplit, User
from app.schemas.transaction import TransactionCreate

def create_transaction(db: Session, tx_in: TransactionCreate) -> Transaction:
    # 1. Den Haupt-Bon erstellen
    db_tx = Transaction(
        title=tx_in.title,
        date=tx_in.date or datetime.utcnow(),
        payer_email=tx_in.payer_email
    )
    db.add(db_tx)
    db.flush()

    # 2. Durch alle Items iterieren
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
        db.flush() # Flushen, um die Item-ID für die Splits zu bekommen

        # 3. Durch alle Splits dieses Items iterieren
        for split_in in item_in.splits:
            user_exists = db.query(User).filter(User.email == split_in.user_email).first()
            if not user_exists:
                raise ValueError(f"User {split_in.user_email} not found")

            db_split = ItemSplit(
                item_id=db_item.id,
                user_email=split_in.user_email,
                amount=split_in.amount
            )
            db.add(db_split)

    db.commit()
    db.refresh(db_tx)
    return db_tx

def get_transactions(db: Session, skip: int = 0, limit: int = 15) -> list[Transaction]:
    return db.query(Transaction)\
        .order_by(Transaction.date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_transaction(db: Session, tx_id: int) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.id == tx_id).first()

def update_transaction(db: Session, tx_id: int, tx_in: TransactionCreate) -> Transaction:
    # Existenzprüfung
    db_tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not db_tx:
        raise ValueError(f"Transaktion mit ID {tx_id} nicht gefunden.")

    try:
        # Kopfdaten der Transaktion aktualisieren
        db_tx.title = tx_in.title
        db_tx.date = tx_in.date or db_tx.date
        db_tx.payer_email = tx_in.payer_email.lower()
        db_tx.source = tx_in.source
        
        # Items und Splits löschen
        db.query(Item).filter(Item.transaction_id == tx_id).delete(synchronize_session=False)
        db.flush()

        # Neue Items und Splits einfügen
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
                user_exists = db.query(User).filter(User.email == split_in.user_email.lower()).first()
                if not user_exists:
                    raise ValueError(f"User {split_in.user_email} existiert nicht.")

                new_split = ItemSplit(
                    item_id=new_item.id,
                    user_email=split_in.user_email.lower(),
                    amount=split_in.amount
                )
                db.add(new_split)

        db.commit()
        db.refresh(db_tx)
        return db_tx

    except Exception as e:
        db.rollback()
        raise e

def delete_transaction(db: Session, tx_id: int) -> bool:
    db_tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not db_tx:
        return False
    try:
        db.delete(db_tx) 
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
