from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.extractor import extract_data
from app.database import get_db
from app.models.db_models import ExtractionRecord

router = APIRouter(prefix="/extract", tags=["extract"])

class ExtractRequest(BaseModel):
    text: str
    doc_type: str | None = None

class ExtractResponse(BaseModel):
    id: int
    doc_type: str
    data: dict

@router.post("/", response_model=ExtractResponse)
async def extract(request: ExtractRequest, db: Session = Depends(get_db)):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    result = await extract_data(request.text, request.doc_type)

    record = ExtractionRecord(
        doc_type=result["doc_type"],
        input_text=request.text,
        result=result["data"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "doc_type": result["doc_type"],
        "data": result["data"]
    }