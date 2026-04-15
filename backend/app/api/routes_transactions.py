from fastapi import APIRouter, Depends, HTTPException, status, Response, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.services.parser import parse_receipt
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
    Aktualisiert die Items + zugehörigen Splits einer Transaktion.
    Alte Items und Splits werden gelöscht durch neue ersetzt.
    """
    
    # Existenzprüfung
    db_tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not db_tx:
        raise HTTPException(
            status_code=404, 
            detail=f"Transaktion mit ID {tx_id} nicht gefunden."
        )

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
    
@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaktion existiert nicht.")
    try:
        db.delete(db_tx) 
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/parse", response_model=TransactionCreate)
async def upload_and_parse_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Nimmt ein PDF oder Bild entgegen, parst die Artikel heraus und
    liefert ein strukturiertes JSON (TransactionCreate) als Entwurf zurück.
    Speichert noch NICHTS in der Datenbank!
    """
    
    # 1. Dateityp validieren (Security Check)
    print('filetype ', file.content_type)
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Dateityp {file.content_type} nicht erlaubt. Nur PDF, JPG oder PNG."
        )

    # 2. Dateigröße limitieren (z.B. max 10 MB) um Memory Leaks zu vermeiden
    file_bytes = await file.read()
    print('len(file_bytes) ', len(file_bytes))
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Die Datei ist zu groß. Maximal 10 MB erlaubt."
        )

    try:
        # 3. Datei parsen (delegiert an den Service)
        parsed_transaction = await parse_receipt(file_bytes, file.content_type)
        print('3. parsed_transaction', parsed_transaction)
        
        # 4. Den Uploader automatisch als 'Payer' des Entwurfs setzen
        parsed_transaction.payer_email = current_user.email
        
        return parsed_transaction

    except ValueError as ve:
        # Fängt Fehler ab, wenn der Parser merkt, dass es z.B. gar kein REWE Bon ist
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Parsen des Dokuments: {str(e)}"
        )