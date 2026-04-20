import logging
from app.services.pdf_receipt_parser import parse_pdf_receipt
from app.services.image_receipt_parser import _parse_image_ocr
from app.schemas.transaction import TransactionCreate

logger = logging.getLogger(__name__)

async def parse_receipt(file_bytes: bytes, mime_type: str) -> TransactionCreate:
    """
    Nimmt den Datei-Stream und leitet ihn an den korrekten Parser weiter.
    Gibt ein Pydantic-Schema zurück, das direkt als 'Entwurf' ans Frontend geht.
    """
    
    file_size = len(file_bytes)
    logger.info(f"Routing receipt parsing... Mime-Type: '{mime_type}', Size: {file_size} bytes.")
    
    try:
        if mime_type == "application/pdf":
            logger.debug("Delegating to PDF parser (sync).")
            result = parse_pdf_receipt(file_bytes)
            logger.info(f"Successfully parsed PDF receipt. Extracted {len(result.items)} items.")
            return result
            
        elif mime_type in ["image/jpeg", "image/png"]:
            logger.debug("Delegating to Image OCR parser (async).")
            result = await _parse_image_ocr(file_bytes)
            
            logger.info(f"Successfully parsed Image receipt. Extracted {len(result.items)} items.")
            return result
        
        else:
            logger.warning(f"Upload rejected: Unsupported mime-type '{mime_type}'.")
            raise ValueError(f"Nicht unterstützter Dateityp: {mime_type}")
            
    except Exception as e:
        logger.error(f"Error during receipt routing/parsing for type '{mime_type}':", exc_info=True)
        raise