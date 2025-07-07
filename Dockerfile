FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Use environment variable to determine what to run
ENV PYTHONPATH=/code

# Default to startup script, but can be overridden
CMD ["./start.sh"]

