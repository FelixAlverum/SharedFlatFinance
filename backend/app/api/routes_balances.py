from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.models import User
from app.schemas.balance import UserBalance
from app.api.deps import get_current_user
from app.repositories import crud_balances

router = APIRouter()

@router.get("/", response_model=List[UserBalance])
def get_balances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ruft die Kontostände aller User ab.
    Die komplette Logik ist in crud_balances ausgelagert.
    """
    return crud_balances.calculate_user_balances(db)