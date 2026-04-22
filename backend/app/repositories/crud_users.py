import logging
from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

# Logger initialisieren
logger = logging.getLogger(__name__)

def get_user_by_email(db: Session, email: str) -> User | None:
    safe_email = email
    logger.debug(f"Suche User mit E-Mail: {safe_email}")
    return db.query(User).filter(User.email == safe_email).first()


def get_all_users(db: Session) -> list[User]:
    logger.debug("Lade alle User aus der Datenbank.")
    return db.query(User).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    safe_email = user_in.email
    logger.info(f"Versuche neuen User anzulegen: {safe_email}")
    
    # Check if user exists
    if get_user_by_email(db, safe_email):
        logger.warning(f"Registrierung fehlgeschlagen: E-Mail '{safe_email}' ist bereits vergeben.")
        raise ValueError("Email already registered")
    
    try:
        hashed_pwd = get_password_hash(user_in.password)
        new_user = User(
            email=safe_email, 
            name=user_in.name, 
            hashed_password=hashed_pwd
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User erfolgreich angelegt (E-Mail: {new_user.email}).")
        return new_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Kritischer Fehler beim Erstellen des Users '{safe_email}': {str(e)}", exc_info=True)
        raise e


def update_user(db: Session, current_user: User, user_update: UserUpdate) -> User:
    logger.info(f"Starte Profil-Update für User: {current_user.name}")
    
    try:
        if user_update.name is not None:
            logger.debug(f"Aktualisiere Namen: '{current_user.name}' -> '{user_update.name}'")
            current_user.name = user_update.name
            
        if user_update.password is not None:
            logger.debug("Aktualisiere Passwort (Hash wird neu generiert).")
            current_user.hashed_password = get_password_hash(user_update.password)
            
        db.commit()
        db.refresh(current_user)
        logger.info(f"User {current_user.name} erfolgreich aktualisiert.")
        return current_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Fehler beim Update von User {current_user.name}: {str(e)}", exc_info=True)
        raise e


def delete_user(db: Session, current_user: User) -> None:
    logger.warning(f"Lösche User {current_user.name} ({current_user.email}) unwiderruflich aus der Datenbank.")
    
    try:
        db.delete(current_user)
        db.commit()
        logger.info(f"User {current_user.name} erfolgreich gelöscht.")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Fehler beim Löschen des Users {current_user.name}: {str(e)}", exc_info=True)
        raise e