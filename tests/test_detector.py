from app.services.extractor import detect_type

def test_detect_invoice():
    text = "Invoice #123, total payment due: $500"
    assert detect_type(text) == "invoice"

def test_detect_email():
    text = "From: john@example.com\nSubject: Meeting tomorrow\nDear team, regards"
    assert detect_type(text) == "email"

def test_detect_resume_default():
    text = "John Doe, Software Engineer with 5 years experience"
    assert detect_type(text) == "resume"