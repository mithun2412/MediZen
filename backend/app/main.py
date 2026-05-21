from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine
from app.models.models import Base
from app.routes import auth, analyze
from app.routes.followup import router as followup_router
from app.reminders_inapp import router as reminder_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MediVoice AI Backend",
    description="AI-powered healthcare assistant API",
    version="2.0.0"
)

# ✅ Handle OPTIONS preflight for ALL routes
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )

# ✅ Add CORS headers to every response
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

app.include_router(auth.router)
app.include_router(analyze.router)

@app.get("/")
def root():
    return {"message": "MediVoice AI Backend v2.0 running ✅"}

@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(followup_router)
app.include_router(reminder_router)
