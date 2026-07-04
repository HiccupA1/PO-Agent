# PO Agent Backend

FastAPI service for the mock Product Owner Agent.

## Run Locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /health`
- `POST /agent/run`
