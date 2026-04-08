from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import hashlib
import base64
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- NEU: Die Pre-Hash Hilfsfunktion ---
def _pre_hash(password: str) -> str:
    """Hasht das Passwort mit SHA-256 vor, um das 72-Byte Limit von bcrypt zu umgehen."""
    # Macht aus JEDEM Passwort einen exakt 44-Zeichen langen (Base64) String
    digest = hashlib.sha256(password.encode('utf-8')).digest()
    return base64.b64encode(digest).decode('ascii')

# --- ANGEPASST: Wir schieben das Passwort erst durch den Pre-Hasher ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_pre_hash(plain_password), hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(_pre_hash(password))

def create_access_token(subject: str) -> str:
    """Erstellt den JWT (Fahrkarte) für den Nutzer."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # "sub" (Subject) ist Standard für "Wer ist dieser Nutzer?" (Wir nutzen die E-Mail)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt