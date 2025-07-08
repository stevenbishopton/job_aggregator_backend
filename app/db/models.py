from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    company_name = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    url = Column(Text, nullable=False, unique=True)
    source = Column(String(512), nullable=False)
    job_id = Column(String(512), nullable=False, index=True)
    publication_date = Column(DateTime, nullable=False)
    tags = Column(Text, nullable=True)
    salary = Column(Text, nullable=True)
    job_type = Column(String(512), nullable=True)
    scraped_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
