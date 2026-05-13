from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.extractor import extract_data
from app.services.pdf_parser import extract_text_from_pdf
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

@router.post("/pdf")
async def extract_from_pdf(
    file: UploadFile = File(...),
    doc_type: str | None = None,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    result = await extract_data(text, doc_type)

    record = ExtractionRecord(
        doc_type=result["doc_type"],
        input_text=text[:1000],
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