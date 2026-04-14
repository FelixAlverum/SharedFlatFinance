from app.services.pdf_receipt_parser import parse_pdf_receipt
from app.schemas.transaction import TransactionCreate

async def parse_receipt(file_bytes: bytes, mime_type: str) -> TransactionCreate:
    """
    Nimmt den Datei-Stream und leitet ihn an den korrekten Parser weiter.
    Gibt ein Pydantic-Schema zurück, das direkt als 'Entwurf' ans Frontend geht.
    """
    
    if mime_type == "application/pdf":
        return parse_pdf_receipt(content)
        
    elif mime_type in ["image/jpeg", "image/png"]:
        return _parse_image_ocr(file_bytes)
    
    else:
        raise ValueError(f"Nicht unterstützter Dateityp: {mime_type}")


def _parse_image_ocr(file_bytes: bytes) -> TransactionCreate:
    """Logik für Handy-Fotos von echten Kassenbons."""
    # image = Image.open(io.BytesIO(file_bytes))
    # text = pytesseract.image_to_string(image, lang='deu')
    
    # HIER: Logik, die den OCR-Text parst...
    
    return TransactionCreate(
        title="Gescanntes Foto",
        payer_email="dummy@wg.com",
        source="camera_scan",
        items=[] 
    )