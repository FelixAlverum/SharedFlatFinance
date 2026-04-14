from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api.deps import get_current_user
from app.models.models import User
from app.services.pdf_receipt_parser import parse_pdf_receipt

router = APIRouter()

@router.post("/upload-receipt")
async def upload_and_parse_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Bitte lade eine PDF-Datei hoch.")
    
    # Die Datei als Bytes lesen
    content = await file.read()
    
    try:
        parsed_data = parse_pdf_receipt(content)
        parsed_data["payer_email"] = current_user.email
        
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Lesen des Bons: {str(e)}")