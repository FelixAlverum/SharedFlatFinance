from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

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
                raise HTTPException(status_code=400, detail=f"User {split_in.user_email} not found")

            db_split = ItemSplit(
                item_id=db_item.id,
                user_email=split_in.user_email,
                amount=split_in.amount
            )
            db.add(db_split)

    db.commit()
    db.refresh(db_tx)
    return db_tx

# --- 2. ALLE KASSENBONS ABRUFEN (Für das Dashboard) ---
@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    skip: int = 0,    # Offset (wieviele überspringen)
    limit: int = 15,  # Wieviele Bons laden
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # .offset() und .limit() sind die SQLAlchemy-Befehle für Paginierung
    transactions = db.query(Transaction)\
        .order_by(Transaction.date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
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

@router.put("/{tx_id}", response_model=TransactionResponse)
def update_transaction(
    tx_id: int,
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aktualisiert eine bestehende Transaktion vollständig.
    Alte Items und Splits werden durch die neuen Daten ersetzt.
    """
    
    # 1. Existenzprüfung
    db_tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not db_tx:
        raise HTTPException(
            status_code=404, 
            detail=f"Transaktion mit ID {tx_id} nicht gefunden."
        )

    # 2. Berechtigungsprüfung (Optional, aber empfohlen)
    # Nur der ursprüngliche Payer oder der aktuelle User darf editieren?
    # if db_tx.payer_email != current_user.email:
    #    raise HTTPException(status_code=403, detail="Nicht autorisiert")

    try:
        # 3. Kopfdaten der Transaktion aktualisieren
        db_tx.title = tx_in.title
        db_tx.date = tx_in.date or db_tx.date
        db_tx.payer_email = tx_in.payer_email.lower() # Case-Insensitivity sicherstellen

        # 4. Bestehende Items löschen
        # Dank cascade="all, delete-orphan" in deinen Modellen werden 
        # die ItemSplits automatisch mitgelöscht.
        db.query(Item).filter(Item.transaction_id == tx_id).delete()
        db.flush() # Änderungen vormerken, um Platz für neue Items zu machen

        # 5. Neue Items und Splits einfügen (Logik analog zu POST)
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
            db.flush() # ID für das neue Item generieren

            for split_in in item_in.splits:
                # Validierung: Existiert der User?
                user_exists = db.query(User).filter(User.email == split_in.user_email.lower()).first()
                if not user_exists:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"User {split_in.user_email} existiert nicht."
                    )

                new_split = ItemSplit(
                    item_id=new_item.id,
                    user_email=split_in.user_email.lower(),
                    amount=split_in.amount
                )
                db.add(new_split)

        # 6. Alles atomar speichern
        db.commit()
        db.refresh(db_tx)
        return db_tx

    except Exception as e:
        db.rollback() # Bei jedem Fehler: Alles rückgängig machen!
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, 
            detail=f"Interner Fehler beim Update: {str(e)}"
        )