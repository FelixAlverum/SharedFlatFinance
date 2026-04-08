from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.models.models import Transaction, Item, ItemSplit, User
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. KASSENBON ERSTELLEN ---
@router.post("/", response_model=TransactionResponse)
def create_transaction(
    tx_in: TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Nur eingeloggte Nutzer dürfen Bons erstellen!
):
    # 1. Den Haupt-Bon erstellen
    db_tx = Transaction(
        title=tx_in.title,
        date=tx_in.date or datetime.utcnow(),
        payer_email=tx_in.payer_email
    )
    db.add(db_tx)
    db.flush() # Wir flushen, um die ID des neuen Bons zu bekommen, ohne schon fest zu speichern (commit)

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
            # Sicherheits-Check: Existiert der User, dem wir Schulden aufschreiben?
            user_exists = db.query(User).filter(User.email == split_in.user_email).first()
            if not user_exists:
                raise HTTPException(status_code=400, detail=f"User {split_in.user_email} not found")

            db_split = ItemSplit(
                item_id=db_item.id,
                user_email=split_in.user_email,
                amount=split_in.amount
            )
            db.add(db_split)

    # 4. Alles zusammen fest in die Datenbank schreiben!
    db.commit()
    db.refresh(db_tx)
    return db_tx

# --- 2. ALLE KASSENBONS ABRUFEN (Für das Dashboard) ---
@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Dashboard nur für Mitbewohner
):
    transactions = db.query(Transaction).order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    return transactions

# --- 3. EINEN EINZELNEN BON ABRUFEN ---
@router.get("/{tx_id}", response_model=TransactionResponse)
def get_transaction(
    tx_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction