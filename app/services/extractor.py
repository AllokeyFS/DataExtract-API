import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "mistral")

PROMPTS = {
    "resume": """Extract information from this resume and return ONLY valid JSON, nothing else.
JSON structure:
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "skills": ["string"],
  "experience": [{"company": "string", "role": "string", "duration": "string"}],
  "education": [{"institution": "string", "degree": "string", "year": "string"}]
}
Resume text:
""",
    "invoice": """Extract information from this invoice and return ONLY valid JSON, nothing else.
JSON structure:
{
  "invoice_number": "string",
  "date": "string",
  "vendor": "string",
  "client": "string",
  "items": [{"description": "string", "quantity": "number", "price": "number"}],
  "total": "number"
}
Invoice text:
""",
    "email": """Extract information from this email and return ONLY valid JSON, nothing else.
JSON structure:
{
  "sender": "string",
  "subject": "string",
  "intent": "string",
  "action_items": ["string"],
  "urgency": "low | medium | high"
}
Email text:
"""
}

async def extract_data(text: str, doc_type: str | None) -> dict:
    if doc_type is None:
        doc_type = detect_type(text)
    
    prompt = PROMPTS.get(doc_type)
    if not prompt:
        raise ValueError(f"Unknown doc_type: {doc_type}")
    
    full_prompt = prompt + text
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False
            }
        )
        response.raise_for_status()
    
    raw = response.json()["response"]
    
    cleaned = raw.strip()
    
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return {"doc_type": doc_type, "data": json.loads(part)}
            except json.JSONDecodeError:
                continue
    
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        cleaned = cleaned[start:end]
    
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse model response as JSON: {e}\nRaw response: {raw}")
    
    return {"doc_type": doc_type, "data": data}

def detect_type(text: str) -> str:
    text_lower = text.lower()
    if any(word in text_lower for word in ["invoice", "total", "payment", "bill"]):
        return "invoice"
    if any(word in text_lower for word in ["subject:", "from:", "dear", "regards"]):
        return "email"
    return "resume"