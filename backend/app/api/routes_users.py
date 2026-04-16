from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. CREATE USER (Registrierung) ---
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(user.password)
    new_user = User(email=user.email, name=user.name, hashed_password=hashed_pwd)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- 2. LOGIN (Generiert den Token) ---
@router.post("/login", response_model=Token)
def login_for_access_token(
    # OAuth2PasswordRequestForm erwartet form-data (username & password)
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # Bei OAuth2 heißt das Feld immer "username", wir nutzen aber die Email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Token erstellen
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

# --- 3. READ (Alle Nutzer abrufen) ---
@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return db.query(User).all()

# --- 4. READ (Das eigene Profil abrufen) ---
# Durch "Depends(get_current_user)" ist diese Route GESPERRT für nicht-eingeloggte!
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
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)
        
    db.commit()
    db.refresh(current_user)
    return current_user

# --- 6. DELETE (Das eigene Profil löschen) ---
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return None