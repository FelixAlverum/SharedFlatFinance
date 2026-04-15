import io
import json
from PIL import Image
from google import genai  # Das neue Paket
from google.genai import types # Für das Schema-Handling
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.schemas.transaction import TransactionCreate
from app.core.config import settings

# 1. Wir definieren ein Hilfs-Schema, wie die KI uns die Daten liefern SOLL
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
    # Zur Sicherheit loggen wir die ersten Zeichen des Keys, um zu prüfen, ob die .env geladen wurde
    print(f"DEBUG: Key starts with: {settings.GEMINI_API_KEY[:5] if settings.GEMINI_API_KEY else 'NONE'}")
    
    # 2. Client init (MUSS in der Funktion oder nach dem Laden der .env passieren)
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    try:
        image = Image.open(io.BytesIO(file_bytes))
    except Exception:
        raise ValueError("Bild konnte nicht gelesen werden. Stelle sicher, dass es ein gültiges JPG/PNG ist.")

    prompt = """
    Analysiere diesen Kassenbon. Extrahiere Geschäft, Datum und alle Artikel.
    Antworte ausschließlich im JSON-Format.
    """

    try:
        # 3. Der neue asynchrone Aufruf via client.aio
        # HINWEIS: Wir nutzen gemini-1.5-flash. Falls Google wieder zickt, geht auch 'gemini-2.0-flash'
        response = await client.aio.models.generate_content(
            model='gemini-flash-latest',
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedReceipt, 
                temperature=0.0
            )
        )
        
        # 4. Das Resultat parsen
        data = response.parsed
        
        # Fallback, falls das neue SDK das Pydantic-Objekt mal nicht sauber entpackt
        if data is None:
            data_dict = json.loads(response.text)
            data = ExtractedReceipt(**data_dict)

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
        raise ValueError(f"KI-Fehler beim Parsen: {str(e)}")