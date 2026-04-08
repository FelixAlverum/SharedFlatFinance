from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.api import routes_users
from app.api import routes_transactions
from app.api import routes_parsing

Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_users.router, prefix="/api/users", tags=["Users"])
app.include_router(routes_transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(routes_parsing.router, prefix="/api/parsing", tags=["Bill Parsing"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}