FROM python:3.12-slim

WORKDIR /app

COPY services/detection-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/detection-service/ .

CMD ["python", "-m", "detection.main"]
