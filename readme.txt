# Allgemein
- code reviews + clean up
- bessere architektur
- db_seed erweitern um transactions, items und itemSplits
- vorhersagen wer was gekauft hat

# feature frontend
- mehrsprachichkeit

# feature backend
- besseres error handling
- requests

# deployment
- portainer
- Eigener server?
- CD implementieren 

# bugs
- bei edit receipt kommt folgender Fehler ! Interner Fehler beim Update: (sqlite3.IntegrityError) FOREIGN KEY constraint failed [SQL: UPDATE transactions SET payer_email=? WHERE transactions.id = ?] [parameters: ('sven@wg.com', 2)] (Background on this error at: https://sqlalche.me/e/20/gkpj)
- Header ohne anmeldung klick auf WGSplit --> dashboard

fertig
- faire aufteilung der positionen
- hässliche popups erstezen
- manueller eintrag
- statisitken einbauen
- dark mode

version: '3.8'

services:
  backend:
    image: alverum/wg_backend:latest
    container_name: wg_backend_prod
    restart: unless-stopped
    ports:
      - "8055:8000"
    volumes:
      - wg_db_data:/app/data  
    environment:
      - GEMINI_API_KEY=[GCP API KEY]
      - SECRET_KEY="HeimlicherKeyDerKurtKoerberWG"
      - SQLALCHEMY_DATABASE_URI="sqlite:///./ledger.db"
      - BACKEND_CORS_ORIGINS='["http://192.168.0.155:3055", "http://localhost:3000", "http://127.0.0.1:3000"]'
      
  frontend:
    image: alverum/wg_frontend:latest
    container_name: wg_frontend_prod
    restart: unless-stopped
    ports:
      - "3055:3000"
    depends_on:
      - backend
    environment:
      - PRIVATE_API_URL=http://backend:8000/api
      - PUBLIC_API_URL=http://192.168.0.155:8055/api 

volumes:
  wg_db_data:
    name: wg_finance_database