import os

from app.routes import (

    conversation,

    uploads,

    analytics
)


from app.routes import reminders


from app.routes import (

    conversation,

    uploads,

    analytics,

    auth
)

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.routes import (

    conversation,

    uploads
)

from fastapi.staticfiles import (
    StaticFiles
)

from app.database import (
    Base,
    engine
)

# ROUTES
from app.routes import (
    conversation
)

# ─────────────────────────────────────────────
# CREATE DATABASE TABLES
# ─────────────────────────────────────────────

Base.metadata.create_all(
    bind=engine
)

# ─────────────────────────────────────────────
# CREATE REQUIRED FOLDERS
# ─────────────────────────────────────────────

os.makedirs(

    "uploads",

    exist_ok=True
)

os.makedirs(

    "reports",

    exist_ok=True
)




# ─────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────

app = FastAPI(

    title="MediZen AI",

    description=(
        "Conversational Multimodal "
        "Healthcare AI Platform"
    ),

    version="1.0.0"
)



app.include_router(

    reminders.router,

    prefix="/api"
)

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# STATIC FILES
# ─────────────────────────────────────────────

# IMAGE UPLOADS
app.mount(

    "/uploads",

    StaticFiles(directory="uploads"),

    name="uploads"
)

# PDF REPORTS
app.mount(

    "/reports",

    StaticFiles(directory="reports"),

    name="reports"
)



app.include_router(

    analytics.router,

    prefix="/api/analytics",

    tags=["Analytics"]
)


app.include_router(

    conversation.router,

    prefix="/api/conversation",

    tags=["Conversation AI"]
)






app.include_router(

    uploads.router,

    prefix="/api/uploads",

    tags=["Uploads"]
)

# ─────────────────────────────────────────────
# ROOT ENDPOINT
# ─────────────────────────────────────────────

@app.get("/")
def root():

    return {

        "message":

            "MediZen AI Backend Running",

        "status":

            "success"
    }

# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.get("/health")
def health_check():

    return {

        "server": "running",

        "ai": "active",

        "database": "connected"
    }


app.include_router(

    auth.router,

    prefix="/api/auth",

    tags=["Authentication"]
)
