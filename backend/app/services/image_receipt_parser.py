import io
import json
import logging
from PIL import Image
from google import genai  # Das neue Paket
from google.genai import types # Für das Schema-Handling
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.schemas.transaction import TransactionCreate
from app.core.config import settings

logger = logging.getLogger(__name__)

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


async def _parse_image_ocr(file_bytes: bytes) -> TransactionCreate:
    logger.info(f"Start parsing image receipt. File size: {len(file_bytes)} bytes.")
    api_key_preview = settings.GEMINI_API_KEY[:5] if settings.GEMINI_API_KEY else 'NONE'
    logger.debug(f"Using Gemini API Key starting with: {api_key_preview}")
    
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    try:
        image = Image.open(io.BytesIO(file_bytes))
        logger.debug(f"Image successfully loaded. Format: {image.format}, Size: {image.size}")
    except Exception as e:
        logger.error(f"Failed to open image: {e}")
        raise ValueError("Bild konnte nicht gelesen werden. Stelle sicher, dass es ein gültiges JPG/PNG ist.")

    prompt = """
    Analysiere diesen Kassenbon. Extrahiere Geschäft, Datum und alle Artikel.
    Antworte ausschließlich im JSON-Format.
    """

    try:
        logger.info("Sending request to Gemini model 'gemini-flash-latest'...")
        start_time = datetime.now()
        
        response = await client.aio.models.generate_content(
            model='gemini-flash-latest',
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedReceipt, 
                temperature=0.0
            )
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Received response from Gemini in {duration:.2f} seconds.")
        
        data = response.parsed
        
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

    except Exception as e:
        logger.error("Error during AI parsing or mapping:", exc_info=True)
        raise ValueError(f"KI-Fehler beim Parsen: {str(e)}")