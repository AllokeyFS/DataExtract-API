from fastapi import FastAPI
from app.routers import extract, history
from app.database import engine
from app.models import db_models

app = FastAPI(
    title="DataExtract API",
    description="Multiformat intelligent data extraction service",
    version="1.0.0"
)

app.include_router(extract.router)
app.include_router(history.router)

@app.on_event("startup")
def startup():
    db_models.Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}