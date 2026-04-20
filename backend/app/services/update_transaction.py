import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from app.models import Transaction, Item, ItemSplit, User
from app.schemas.transaction import TransactionCreate

# Logger initialisieren
logger = logging.getLogger(__name__)

async def update_full_transaction(
    db: AsyncSession, 
    transaction_id: int, 
    data: TransactionCreate
):
    logger.info(f"Starte Update für Transaktion ID {transaction_id}")

    # Transaktion laden
    result = await db.execute(
        select(Transaction).filter(Transaction.id == transaction_id)
    )
    db_transaction = result.scalars().first()
    
    if not db_transaction:
        logger.error(f"Update fehlgeschlagen: Transaktion ID {transaction_id} existiert nicht.")
        raise ValueError("Transaktion nicht gefunden")

    # Bezahler validieren
    user_result = await db.execute(select(User).filter(User.email == data.payer_email))
    if not user_result.scalars().first():
        logger.warning(f"Update abgebrochen: Nutzer '{data.payer_email}' nicht im System.")
        raise ValueError(f"Nutzer mit der E-Mail {data.payer_email} existiert nicht im System.")
    
    # Kopfdaten aktualisieren
    db_transaction.title = data.title
    db_transaction.date = data.date
    db_transaction.payer_email = data.payer_email

    logger.debug(f"Kopfdaten aktualisiert. Ersetze nun die Items...")

    # Alte Items löschen (Delete & Re-insert vermeidet komplexes Diffing)
    await db.execute(delete(Item).where(Item.transaction_id == transaction_id))

    # Items und Splits neu anlegen
    for item_data in data.items:
        new_item = Item(
            name=item_data.name,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_data.total_price,
            category=item_data.category,
            transaction_id=transaction_id
        )
        db.add(new_item)
        await db.flush()  # ID für das neue Item generieren

        for split_data in item_data.splits:
            new_split = ItemSplit(
                item_id=new_item.id,
                user_email=split_data.user_email,
                amount=split_data.amount
            )
            db.add(new_split)

    # Speichern und neu laden
    await db.commit()
    await db.refresh(db_transaction)
    
    logger.info(f"Erfolgreich aktualisiert: Transaktion ID {transaction_id} ({len(data.items)} Items).")
    return db_transaction