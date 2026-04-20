import logging
import io
import re
import pdfplumber
from datetime import datetime, timezone
from app.schemas.transaction import TransactionCreate

logger = logging.getLogger(__name__)

def parse_pdf_receipt(file_content: bytes) -> TransactionCreate:
    logger.info(f"Starte PDF-Parsing. Dateigröße: {len(file_content)} Bytes.")
    
    items = []
    item_pattern = re.compile(r'^(.*?)\s+(-?\d+,\d{2})\s*([AB])\s*\*?$')
    qty_pattern = re.compile(r'^(\d+)\s*Stk\s*x\s*(-?\d+,\d{2})?$')

    has_started = False 
    pending_name = "" 

    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            logger.debug(f"PDF erfolgreich geöffnet. {len(pdf.pages)} Seite(n) gefunden.")
            pages_text = [page.extract_text() or "" for page in pdf.pages]
            text = "\n".join(pages_text)
            
    except Exception as e:
        logger.error("Kritischer Fehler: PDF konnte nicht von pdfplumber verarbeitet werden.", exc_info=True)
        raise ValueError(f"Die Datei konnte nicht als PDF gelesen werden. Details: {str(e)}")

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    logger.debug(f"Text extrahiert: {len(lines)} nicht-leere Zeilen zu prüfen.")

    for i, line in enumerate(lines):
        if not has_started:
            if line.upper() == "EUR":
                logger.debug(f"Start-Markierung 'EUR' in Zeile {i} gefunden. Beginne Artikel-Extraktion.")
                has_started = True
            continue

        if "-------------------------------------" in line:
            logger.debug(f"End-Markierung '---' in Zeile {i} gefunden. Beende Extraktion.")
            break

        item_match = item_pattern.search(line)
        if item_match:
            name_part = item_match.group(1).strip()
            total_price = float(item_match.group(2).replace(',', '.'))
            
            full_name = f"{pending_name} {name_part}".strip() if pending_name else name_part
            pending_name = ""
            
            items.append({
                "name": full_name,
                "quantity": 1.0,
                "unit_price": total_price,
                "total_price": total_price,
                "category": "Lebensmittel",
                "splits": []
            })
            continue

        qty_match = qty_pattern.search(line)
        if qty_match and len(items) > 0:
            qty = float(qty_match.group(1))
            unit_price_str = qty_match.group(2)
            
            last_item = items[-1]
            last_item["quantity"] = qty
            
            if unit_price_str:
                last_item["unit_price"] = float(unit_price_str.replace(',', '.'))
            else:
                if qty > 0:
                    last_item["unit_price"] = round(last_item["total_price"] / qty, 2)
                else:
                    logger.warning(f"Warnung: Menge 0 gefunden für '{last_item['name']}'. Setze Einzelpreis = Gesamtpreis.")
                    last_item["unit_price"] = last_item["total_price"]
            
            logger.debug(f"Menge aktualisiert für '{last_item['name']}': {qty}x")
            continue

        is_tax_line = line.startswith("A=") or line.startswith("B=") or "Steuer" in line
        if not is_tax_line and "EUR" not in line and "Geg." not in line:
            if pending_name:
                pending_name += " " + line
            else:
                pending_name = line

    logger.info(f"PDF-Parsing abgeschlossen. {len(items)} Artikel extrahiert.")

    return TransactionCreate(
        title="Wocheneinkauf REWE",
        date=datetime.now(timezone.utc),
        payer_email="dummy@wg.com", 
        source="pdf_scan",
        items=items
    )