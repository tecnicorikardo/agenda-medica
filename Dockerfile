FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY frontend /app/frontend
COPY logo.png /app/logo.png
COPY private_key.pem /app/private_key.pem
COPY public_key.pem /app/public_key.pem

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

