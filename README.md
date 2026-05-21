# MediVoice AI

A starter AI project with a React frontend and FastAPI backend.

## Structure

- `frontend/` - React application built with Vite
- `backend/` - FastAPI backend service
- `docker-compose.yml` - Local development Docker setup
- `.github/workflows/ci.yml` - CI workflow for build/test

## Local development

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Backend

```powershell
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose

```powershell
docker compose up --build
```
