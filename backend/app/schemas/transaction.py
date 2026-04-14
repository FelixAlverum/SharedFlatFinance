from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# ==========================================
# 1. SPLIT SCHEMAS
# ==========================================
class ItemSplitBase(BaseModel):
    user_email: EmailStr 
    amount: float = Field(...)

class ItemSplitCreate(ItemSplitBase):
    pass

class ItemSplitResponse(ItemSplitBase):
    id: int
    
    class Config:
        from_attributes = True # Erlaubt Pydantic, SQLAlchemy-Modelle zu lesen (früher: orm_mode)


# ==========================================
# 2. ITEM SCHEMAS
# ==========================================
class ItemBase(BaseModel):
    name: str
    quantity: float = 1.0
    unit_price: float
    total_price: float
    category: Optional[str] = None

class ItemCreate(ItemBase):
    splits: List[ItemSplitCreate] # Nutzt das Create-Schema der Splits

class ItemResponse(ItemBase):
    id: int
    splits: List[ItemSplitResponse] # Nutzt das Response-Schema der Splits
    
    class Config:
        from_attributes = True


# ==========================================
# 3. TRANSACTION SCHEMAS
# ==========================================
class TransactionBase(BaseModel):
    title: str
    date: Optional[datetime] = None
    payer_email: EmailStr
    source: str = Field(default="rewe_scan", description="Herkunft: 'manual' oder 'rewe_scan'")

class TransactionCreate(TransactionBase):
    items: List[ItemCreate] # Liste der Items beim Erstellen

class TransactionResponse(TransactionBase):
    id: int
    date: datetime 
    items: List[ItemResponse]
    
    class Config:
        from_attributes = True