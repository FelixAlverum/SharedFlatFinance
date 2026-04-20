from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from app.models import Transaction, Item, ItemSplit
from app.models import User

async def update_full_transaction(
    db: AsyncSession, 
    transaction_id: int, 
    data: TransactionUpdate
):
    # 1. Bestehende Transaktion laden
    result = await db.execute(
        select(Transaction).filter(Transaction.id == transaction_id)
    )
    db_transaction = result.scalars().first()
    
    if not db_transaction:
        raise ValueError("Transaktion nicht gefunden")

    user_result = await db.execute(select(User).filter(User.email == data.payer_email))
    if not user_result.scalars().first():
        raise ValueError(f"Nutzer mit der E-Mail {data.payer_email} existiert nicht im System.")
    
    # 2. Kopfdaten aktualisieren
    db_transaction.title = data.title
    db_transaction.date = data.date
    db_transaction.payer_email = data.payer_email

    # 3. Effizientes Management der Items: Bestehende löschen und neu anlegen
    # Grund: Diffing von Item-IDs und deren Splits ist fehleranfällig. 
    # Ein sauberer Re-Insert der Items garantiert Konsistenz mit dem UI-State.
    await db.execute(delete(Item).where(Item.transaction_id == transaction_id))

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

        # 4. Splits für dieses Item anlegen
        for split_data in item_data.splits:
            new_split = ItemSplit(
                item_id=new_item.id,
                user_email=split_data.user_email,
                amount=split_data.amount
            )
            db.add(new_split)

    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction