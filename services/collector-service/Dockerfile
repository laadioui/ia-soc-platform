FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/collector-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/collector-service/ .

EXPOSE 8000

# Single worker by default: the demo runs on SQLite, where concurrent writers
# would contend. Scale with WEB_CONCURRENCY only on a real database backend.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-1}
