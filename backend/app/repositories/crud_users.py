from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def create_user(db: Session, user_in: UserCreate) -> User:
    # Check if user exists
    if get_user_by_email(db, user_in.email):
        raise ValueError("Email already registered")
    
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, name=user_in.name, hashed_password=hashed_pwd)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, current_user: User, user_update: UserUpdate) -> User:
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)
        
    db.commit()
    db.refresh(current_user)
    return current_user

def delete_user(db: Session, current_user: User) -> None:
    db.delete(current_user)
    db.commit()
