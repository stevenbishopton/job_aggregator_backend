from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.db.models import Base
from app.api.jobs import router as jobs_router
import os
from dotenv import load_dotenv

load_dotenv()

# Dev only: auto-create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Aggregator API",
    description="Fetches, stores, and serves jobs from multiple sources",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(jobs_router, prefix="/api", tags=["Jobs"])
