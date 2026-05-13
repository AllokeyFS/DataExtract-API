from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class ExtractionRecord(Base):
    __tablename__ = "extractions"

    id = Column(Integer, primary_key=True, index=True)
    doc_type = Column(String, nullable=False)
    input_text = Column(String, nullable=False)
    result = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())