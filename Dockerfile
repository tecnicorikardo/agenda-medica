FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic
COPY backend /app/backend
COPY frontend /app/frontend
COPY logo.png /app/logo.png

ENV PYTHONUNBUFFERED=1

# Roda migrations e depois sobe o servidor
CMD ["sh", "-c", "python -m backend.scripts.migrate && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
