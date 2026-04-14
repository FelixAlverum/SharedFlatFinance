import io
import re
import pdfplumber

def parse_pdf_receipt(file_content: bytes) -> dict:
    items = []
    # Sucht in EINER Zeile: Alles (Name), dann den Preis (z.B. 2,29), dann A oder B, dann evtl. ein Sternchen
    item_pattern = re.compile(r'^(.*?)\s+(-?\d+,\d{2})\s*([AB])\s*\*?$')
    
    # Sucht Mengen wie: "2 Stk x 1,49" oder nur "2 Stk x"
    qty_pattern = re.compile(r'^(\d+)\s*Stk\s*x\s*(-?\d+,\d{2})?$')

    has_started = False 
    pending_name = "" # Falls ein Name mal so lang ist, dass er über 2 Zeilen geht

    with pdfplumber.open(io.BytesIO(file_content)) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    for line in lines:
        if not has_started:
            if line.upper() == "EUR":
                has_started = True
            continue

        if "SUMME" in line.upper():
            break

        # 1. IST ES EIN PRODUKT? (z.B. "FRZ.SCHOKOBROET. 2,29 B")
        item_match = item_pattern.search(line)
        if item_match:
            name_part = item_match.group(1).strip()
            total_price = float(item_match.group(2).replace(',', '.'))
            
            # Falls wir aus der vorherigen Zeile noch einen Namens-Teil übrig haben
            full_name = f"{pending_name} {name_part}".strip() if pending_name else name_part
            pending_name = "" # Zurücksetzen
            
            # Wir speichern das Produkt erstmal mit Menge 1
            items.append({
                "name": full_name,
                "quantity": 1.0,
                "unit_price": total_price,
                "total_price": total_price,
                "category": "Lebensmittel",
                "splits": []
            })
            continue

        # 2. IST ES EINE MENGENANGABE? (z.B. "2 Stk x 1,49")
        qty_match = qty_pattern.search(line)
        if qty_match and len(items) > 0:
            qty = float(qty_match.group(1))
            unit_price_str = qty_match.group(2)
            
            # Wir holen uns das LETZTE Produkt, das wir gespeichert haben, und korrigieren es!
            last_item = items[-1]
            last_item["quantity"] = qty
            
            if unit_price_str:
                last_item["unit_price"] = float(unit_price_str.replace(',', '.'))
            else:
                last_item["unit_price"] = round(last_item["total_price"] / qty, 2)
            continue

        # 3. IST ES NUR EIN NAME? (Wenn der Name in der nächsten Zeile weitergeht)
        is_tax_line = line.startswith("A=") or line.startswith("B=") or "Steuer" in line
        if not is_tax_line and "EUR" not in line and "Geg." not in line:
            if pending_name:
                pending_name += " " + line
            else:
                pending_name = line

    return {
        "title": "Wocheneinkauf REWE",
        "items": items
    }