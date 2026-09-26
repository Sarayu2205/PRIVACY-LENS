# PrivacyLens Backend

FastAPI backend for PrivacyLens.

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
copy ..\.env.example .env   # then edit .env
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs
