from fastapi import APIRouter, Depends, HTTPException, status, Response, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from app.services.parser import parse_receipt
from app.db.session import get_db
from app.models.models import User
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.api.deps import get_current_user
from app.repositories import crud_transactions

router = APIRouter()

# --- 1. KASSENBON ERSTELLEN ---
@router.post("/", response_model=TransactionResponse)
def create_transaction(
    tx_in: TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Nur eingeloggte Nutzer dürfen Bons erstellen!
):
    try:
        return crud_transactions.create_transaction(db, tx_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interner Fehler: {str(e)}")


# --- 2. ALLE KASSENBONS ABRUFEN (Für das Dashboard) ---
@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    skip: int = 0,    # Offset (wieviele überspringen)
    limit: int = 15,  # Wieviele Bons laden
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_transactions.get_transactions(db, skip=skip, limit=limit)


# --- 3. EINEN EINZELNEN BON ABRUFEN ---
@router.get("/{tx_id}", response_model=TransactionResponse)
def get_transaction(
    tx_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = crud_transactions.get_transaction(db, tx_id)
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
    try:
        return crud_transactions.update_transaction(db, tx_id, tx_in)
    except ValueError as e:
        raise HTTPException(status_code=404 if "nicht gefunden" in str(e) else 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interner Fehler beim Update: {str(e)}")

    
@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        success = crud_transactions.delete_transaction(db, tx_id)
        if not success:
            raise HTTPException(status_code=404, detail="Transaktion existiert nicht.")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
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
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Dateityp {file.content_type} nicht erlaubt. Nur PDF, JPG oder PNG."
        )

    # 2. Dateigröße limitieren (z.B. max 10 MB) um Memory Leaks zu vermeiden
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Die Datei ist zu groß. Maximal 10 MB erlaubt."
        )

    try:
        # 3. Datei parsen (delegiert an den Service)
        parsed_transaction = await parse_receipt(file_bytes, file.content_type)
        
        # 4. Den Uploader automatisch als 'Payer' des Entwurfs setzen
        parsed_transaction.payer_email = current_user.email
        
        return parsed_transaction

    except ValueError as ve:
        # Fängt Fehler ab, wenn der Parser merkt, dass es z.B. gar kein REWE Bon ist
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Parsen des Dokuments: {str(e)}"
        )