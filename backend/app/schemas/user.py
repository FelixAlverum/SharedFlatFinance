from pydantic import BaseModel, EmailStr

# 1. Das Format, in dem das Frontend uns einen neuen Nutzer schickt
class UserCreate(BaseModel):
    email: EmailStr  # Validiert automatisch, ob ein '@' enthalten ist!
    name: str
    password: str

# 2. Das Format, in dem wir den Nutzer ans Frontend ZURÜCK senden
class UserResponse(BaseModel):
    email: str
    name: str
    # Beachte: Kein Passwort hier!

    class Config:
        from_attributes = True  # Erlaubt Pydantic, SQLAlchemy-Objekte zu lesen