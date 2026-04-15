# 1. Wir starten mit einem offiziellen, schlanken Python 3.11 Image
FROM python:3.11-slim

# 2. Wir setzen das Arbeitsverzeichnis INNERHALB des Containers
WORKDIR /app

# 3. System-Abhängigkeiten installieren (wichtig für OCR/Bildverarbeitung und SQLite)
RUN apt-get update && apt-get install -y \
    gcc \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Requirements kopieren und installieren
# (Wir machen das VOR dem restlichen Code, damit Docker diesen Schritt 
# cachen kann, falls sich nur dein Code, aber nicht die Pakete ändern)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Den gesamten restlichen Code in den Container kopieren
COPY . .

# 6. Wir sagen Docker, auf welchem Port die App lauscht
EXPOSE 8000

# 7. Der Startbefehl für den Server
# WICHTIG: host 0.0.0.0 ist in Docker zwingend nötig, 
# damit der Server auch Zugriffe von "außerhalb" des Containers zulässt!
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]