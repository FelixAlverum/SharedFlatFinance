import io
import os
import json
import logging
from PIL import Image, ImageEnhance
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from ollama import AsyncClient

from app.schemas.transaction import TransactionCreate
from app.core.config import settings

logger = logging.getLogger(__name__)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")

class ExtractedItem(BaseModel):
    name: str = Field(description="Name des Artikels, z.B. 'Milch 3,5%'")
    quantity: float = Field(description="Anzahl. Wenn nicht angegeben, dann 1.0")
    unit_price: float = Field(description="Einzelpreis in Euro")
    total_price: float = Field(description="Gesamtpreis der Position in Euro")
    category: str = Field(description="Kategorie wie Lebensmittel, Haushalt, Getränke, Drogerie")

class ExtractedReceipt(BaseModel):
    title: str = Field(description="Name des Geschäfts, z.B. REWE, Edeka, Aldi")
    date: str | None = Field(default=None, description="Datum im Format YYYY-MM-DD")
    items: list[ExtractedItem]

def _preprocess_image(file_bytes: bytes) -> bytes:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        
        # Bild Schwarz-Weiß (Graustufen) färben
        image = image.convert("L") 
        
        # 2. Kontrast stark erhöhen
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0) 
        
        # 3. Speicherplatz drastisch reduzieren
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=70, optimize=True) 
        
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Fehler bei der Bildvorverarbeitung: {e}")
        raise ValueError("Fehler bei der Bildvorverarbeitung. Stelle sicher, dass es ein gültiges JPG/PNG ist.")


async def _parse_image_ocr(file_bytes: bytes) -> TransactionCreate:
    """
    Analysiert ein Kassenzettel-Bild mit dem lokalen Moondream2 Modell über Ollama.
    Nutzt Guided Generation via Pydantic JSON Schema.
    """
    client = AsyncClient(host=OLLAMA_HOST)
    file_bytes = _preprocess_image(file_bytes)
    logger.info(f"Start parsing image receipt. File size: {len(file_bytes)} bytes.")
        
    try:
        image = Image.open(io.BytesIO(file_bytes))
        logger.debug(f"Image successfully loaded. Format: {image.format}, Size: {image.size}")
    except Exception as e:
        logger.error(f"Failed to open image: {e}")
        raise ValueError("Bild konnte nicht gelesen werden. Stelle sicher, dass es ein gültiges JPG/PNG ist.")

    # Der Prompt kann jetzt viel kürzer sein, da das Schema über die API erzwungen wird
    prompt = "Analysiere das angehängte Bild des Kassenzettels und extrahiere die Daten."

    try:
        logger.info("Sending request to moondream ...")
        start_time = datetime.now()
        
        response = await client.chat(
            model='moondream', # Standard-Tag für Moondream 2 in Ollama
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [file_bytes]
            }],
            # Hier passiert die Magie: Wir übergeben das Pydantic-Schema!
            format=ExtractedReceipt.model_json_schema(), 
            options={
                "temperature": 0.0 # Wichtig für verlässliche Datenextraktion
            }
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        raw_content = response['message']['content']
        
        logger.info(f"Received response from moondream in {duration:.2f} seconds.")
        logger.debug(f"Raw Output: {raw_content}")

        # Pydantic validiert den String direkt in deine Python-Objekte
        data = ExtractedReceipt.model_validate_json(raw_content)

        logger.info(f"Successfully extracted receipt from '{data.title}' with {len(data.items)} items.")

        # Mapping auf dein TransactionCreate Schema
        extracted_items = []
        for item in data.items:
            extracted_items.append({
                "name": item.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "category": item.category,
                "splits": [] # Bleibt leer, macht der User später!
            })

        return TransactionCreate(
            title=data.title,
            date=datetime.now(timezone.utc), # Alternativ: data.date falls gewünscht
            payer_email="dummy@wg.com",
            source="camera_scan",
            items=extracted_items
        )

    except Exception as e:
        logger.error("Error during AI parsing or mapping:", exc_info=True)
        raise ValueError(f"KI-Fehler beim Parsen mit Moondream: {str(e)}")