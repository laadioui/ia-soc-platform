FROM python:3.12-slim

WORKDIR /app

COPY services/notification-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/notification-service/ .

CMD ["python", "-m", "app.main"]
