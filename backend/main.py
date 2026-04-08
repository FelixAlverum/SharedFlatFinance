from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base

# This ensures all our database tables are created when the app starts
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# --- CORS SETUP ---
# This allows your SvelteKit app (running on port 5173) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTES ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Shared Flat Ledger API!"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "database": "connected"}