from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import ExtractionRecord

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/")
def get_history(limit: int = 10, db: Session = Depends(get_db)):
    records = db.query(ExtractionRecord)\
                .order_by(ExtractionRecord.created_at.desc())\
                .limit(limit)\
                .all()
    return [
        {
            "id": r.id,
            "doc_type": r.doc_type,
            "created_at": r.created_at,
            "result": r.result
        }
        for r in records
    ]

@router.get("/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(ExtractionRecord).filter(ExtractionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "id": record.id,
        "doc_type": record.doc_type,
        "input_text": record.input_text,
        "created_at": record.created_at,
        "result": record.result
    }