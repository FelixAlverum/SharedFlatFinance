from pydantic import BaseModel
from typing import List

class UserTotalSpend(BaseModel):
    name: str
    total_spend: float

class PopularItem(BaseModel):
    name: str
    buy_count: int
    total_spend: float

class TimeSeriesData(BaseModel):
    period: str  # z.B. "2023-10" für Oktober 2023
    amount: float

class CategorySpend(BaseModel):
    category: str
    amount: float