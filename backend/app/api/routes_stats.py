from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User
from app.api.deps import get_current_user
from app.schemas import stats as schemas
from app.repositories import crud_stats

router = APIRouter()

# --- 1. GESAMTE AUSGABEN PRO USER ---
@router.get("/total-spend", response_model=list[schemas.UserTotalSpend])
def get_total_spend(db: Session = Depends(get_db)):
    return crud_stats.get_total_spend(db)

# --- 2. BELIEBTESTE ITEMS EINES USERS ---
@router.get("/popular-items")
def get_popular_items(db: Session = Depends(get_db)):
    """Zeigt alle Produkte an, aufgeschlüsselt nach JEDEM User (ohne Pfand!)"""
    return crud_stats.get_popular_items(db)

# --- 3. ZEITLICHER VERLAUF ---
@router.get("/spending-over-time", response_model=list[schemas.TimeSeriesData])
def get_spending_over_time(
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_stats.get_spending_over_time(db, user_email=current_user.email, year=year)

# --- 4. KATEGORIEN ---
@router.get("/category-spend", response_model=list[schemas.CategorySpend])
def get_category_spend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_stats.get_category_spend(db, user_email=current_user.email)