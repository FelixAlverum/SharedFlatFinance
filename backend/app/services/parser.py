from app.services.pdf_receipt_parser import parse_pdf_receipt
from app.services.image_receipt_parser import _parse_image_ocr
from app.schemas.transaction import TransactionCreate

async def parse_receipt(file_bytes: bytes, mime_type: str) -> TransactionCreate:
    """
    Nimmt den Datei-Stream und leitet ihn an den korrekten Parser weiter.
    Gibt ein Pydantic-Schema zurück, das direkt als 'Entwurf' ans Frontend geht.
    """
    
    if mime_type == "application/pdf":
        return parse_pdf_receipt(file_bytes)
        
    elif mime_type in ["image/jpeg", "image/png"]:
        return _parse_image_ocr(file_bytes)
    
    else:
        raise ValueError(f"Nicht unterstützter Dateityp: {mime_type}")
