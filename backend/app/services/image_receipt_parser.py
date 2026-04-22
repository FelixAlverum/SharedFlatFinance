import io
import json
import logging
from PIL import Image, ImageEnhance
from google import genai  # Das neue Paket
from google.genai import types # Für das Schema-Handling
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
    Analysiert ein Kassenzettel-Bild mit dem lokalen Gemma 4 E2B Modell über Ollama.
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

    prompt = """
    Du bist ein intelligenter Finanz-Assistent für eine Wohngemeinschaft.
    Analysiere das angehängte Bild des Kassenzettels.
    
    Extrahiere die Daten in exakt diesem JSON-Format:
    {
      "title": "Name des Geschäfts (z.B. REWE, ALDI)",
      "items": [
        {
          "name": "Artikelname",
          "quantity": 1,
          "unit_price": 0.00,
          "total_price": 0.00,
          "category": "Kategorie"
        }
      ]
    }
    Gib AUSSCHLIESSLICH validiertes JSON zurück. Keinen weiteren Text.
    """

    try:
        logger.info("Sending request to Gemini model 'gemini-flash-latest'...")
        start_time = datetime.now()
        
        response = await client.chat(
            model='gemma4:e2b',
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [file_bytes]
            }],
            format='json', # Zwingt Ollama, JSON auszugeben
            options={
                "temperature": 0.0 # Wichtig: 0.0 für deterministische, verlässliche Extraktion
            }
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Received response from local Gemma 4 in {duration:.2f} seconds.")
        
        content = response['message']['content'].strip()

        # Sicherheits-Cleanup: Falls das Modell Markdown-Ticks (```json) mitschickt
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        content = content.strip()
        
        # JSON parsen und an das Backend zurückgeben
        parsed_data = json.loads(content)
        
        data = parsed_data
        
        if data is None:
            logger.warning("response.parsed was None. Falling back to manual JSON parsing.")
            data_dict = json.loads(response.text)
            data = ExtractedReceipt(**data_dict)

        logger.info(f"Successfully extracted receipt from '{data.title}' with {len(data.items)} items.")

        # 5. Mapping auf dein TransactionCreate Schema
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
            date=datetime.now(timezone.utc),
            payer_email="dummy@wg.com",
            source="camera_scan",
            items=extracted_items
        )

    except json.JSONDecodeError as e:
        logger.error(f"Fehler beim Parsen der Ollama-Antwort: {content} - Error: {e}")
        raise ValueError("Gemma 4 hat kein valides JSON zurückgegeben.")
    except Exception as e:
        logger.error(f"Ollama API Fehler: {e}")
        raise RuntimeError(f"Fehler bei der Kommunikation mit dem KI-Modell: {str(e)}")