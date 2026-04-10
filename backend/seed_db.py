from app.db.session import SessionLocal
from app.models.models import User
# Angenommen, du hast eine pwd_context Instanz für bcrypt
from app.core.security import get_password_hash 

def seed_users():
    db = SessionLocal()
    test_hash = get_password_hash("password123")
    
    users = [
        User(email="felix@mail.com",    name="Felix",       hashed_password=test_hash),
        User(email="nico@wg.com",       name="Nic0",        hashed_password=test_hash),
        User(email="sven@example.com",  name="Svenjamin",   hashed_password=test_hash),
        User(email="mark@example.com",  name="marK",        hashed_password=test_hash),
    ]

    try:
        for u in users:
            exists = db.query(User).filter(User.email == u.email).first()
            if not exists:
                db.add(u)
        
        db.commit()
        print("✅ 4 Test-User wurden erfolgreich angelegt (Passwort: password123)")
    except Exception as e:
        print(f"❌ Fehler beim Seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()