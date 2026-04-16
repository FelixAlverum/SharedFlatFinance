zum starten in commandline
1. navigation in /backend
2. venv aktivieren mit      .\venv\Scripts\activate
3. app starten mit          uvicorn main:app --reload
4. bei neuer db             python -m seed_db

.env file erstellen mit 
GEMINI_API_KEY= <GEMINI_API_KEY aus https://aistudio.google.com/api-keys>
SQLALCHEMY_DATABASE_URI="sqlite:///./ledger.db"
BACKEND_CORS_ORIGINS='["http://192.168.178.50:8000", "http://localhost:8000", "http://localhost:3000", "http://127.0.0.1:3000"]'
SECRET_KEY= "HierDerSecretKeyDeinerWahl"