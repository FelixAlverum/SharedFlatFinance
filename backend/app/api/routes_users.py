from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_user
from app.repositories import crud_users

router = APIRouter()

# --- 1. CREATE USER (Registrierung) ---
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return crud_users.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- 2. LOGIN (Generiert den Token) ---
@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_email(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

# --- 3. READ (Alle Nutzer abrufen) ---
@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return crud_users.get_all_users(db)

# --- 4. READ (Das eigene Profil abrufen) ---
@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- 5. UPDATE (Das eigene Profil bearbeiten) ---
@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return crud_users.update_user(db, current_user, user_update)

# --- 6. DELETE (Das eigene Profil löschen) ---
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    crud_users.delete_user(db, current_user)
    return None