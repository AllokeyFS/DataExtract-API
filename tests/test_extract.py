from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.database import engine
from app.models import db_models

# Создаём таблицы перед тестами
db_models.Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_extract_empty_text():
    response = client.post("/extract/", json={"text": "", "doc_type": "resume"})
    assert response.status_code == 400

@patch("app.routers.extract.extract_data", new_callable=AsyncMock)
def test_extract_resume(mock_extract):
    mock_extract.return_value = {
        "doc_type": "resume",
        "data": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": None,
            "skills": ["Python"],
            "experience": [],
            "education": []
        }
    }
    response = client.post(
        "/extract/",
        json={
            "text": "John Doe, Python developer",
            "doc_type": "resume"
        }
    )
    assert response.status_code == 200
    assert response.json()["doc_type"] == "resume"
    assert "data" in response.json()