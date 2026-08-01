# MediZen AI — Intelligent Healthcare Assistant

MediZen AI is an intelligent healthcare assistant that helps users understand symptoms, analyse medical reports, manage medications, monitor health progress, and find nearby hospitals in one place.

It brings together 6+ healthcare workflows, including AI-guided symptom follow-ups with 3-level risk assessment, OCR/PDF report analysis, medication reminders, adherence tracking, health analytics, and hospital recommendations.

## Features

- **AI health chat:** Guided symptom conversations and low, moderate, or high risk assessment.
- **Medical report analysis:** Upload PDF reports or images for OCR extraction and AI-assisted analysis.
- **Medication management:** Create reminders, track doses, and monitor adherence.
- **Health analytics:** View health scores, symptom trends, and medication progress.
- **Report history:** Revisit uploaded reports and generated assessments.
- **Hospital recommendations:** Find suitable nearby hospitals based on symptoms and location.

## Technology

Python · FastAPI · React.js · PostgreSQL · LLM · RAG · FAISS · OCR · NLP

## Project structure

- `frontend/` — React application built with Vite.
- `backend/` — FastAPI API, AI services, RAG pipeline, and database models.
- `docker-compose.yml` — Local Docker development setup.
- `.github/workflows/ci.yml` — Frontend build and backend test workflow.

## Local development

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL

### Backend

```powershell
cd backend
Copy-Item .env.example .env
# Update DATABASE_URL and GROQ_API_KEY in .env
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API runs at `http://localhost:8000`. Open `http://localhost:8000/docs` for the interactive API documentation.

### Frontend

In a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite prints the local application URL, usually `http://localhost:5173`.

### Docker Compose

Configure the required environment variables, then run:

```powershell
docker compose up --build
```

## Testing

```powershell
cd backend
pytest
```
