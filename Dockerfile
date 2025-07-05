FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . .

# Use the PORT environment variable that Render provides
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]

ENV PYTHONPATH=/code

