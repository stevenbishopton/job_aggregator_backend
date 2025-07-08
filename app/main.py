from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.db.models import Base
from app.api.jobs import router as jobs_router
import os
from dotenv import load_dotenv

load_dotenv()

# Only create tables in development
if os.getenv("ENVIRONMENT", "development") == "development":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Aggregator API",
    description="Fetches, stores, and serves jobs from multiple sources",
    version="1.0.0"
)

# CORS setup - update with your frontend URL in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://job-aggregator-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(jobs_router, prefix="/api", tags=["Jobs"])
