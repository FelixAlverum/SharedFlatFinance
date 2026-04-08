from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- INPUT SCHEMAS (Was das Frontend uns schickt) ---

class ItemSplitCreate(BaseModel):
    user_email: str
    amount: float

class ItemCreate(BaseModel):
    name: str
    quantity: float = 1.0
    unit_price: float
    total_price: float
    category: Optional[str] = None
    splits: List[ItemSplitCreate] # Eine Liste der Aufteilungen für DIESES Produkt

class TransactionCreate(BaseModel):
    title: str
    date: Optional[datetime] = None # Wenn nichts kommt, nimmt die DB das aktuelle Datum
    payer_email: str
    items: List[ItemCreate] # Eine Liste aller Produkte auf dem Bon


# --- OUTPUT SCHEMAS (Was wir ans Frontend zurücksenden) ---

class ItemSplitResponse(BaseModel):
    id: int
    user_email: str
    amount: float
    class Config:
        from_attributes = True

class ItemResponse(BaseModel):
    id: int
    name: str
    quantity: float
    unit_price: float
    total_price: float
    category: Optional[str]
    splits: List[ItemSplitResponse]
    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: int
    title: str
    date: datetime
    payer_email: str
    items: List[ItemResponse]
    class Config:
        from_attributes = True