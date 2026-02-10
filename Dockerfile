FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data.py .
COPY simulation.py .
COPY app.py .
COPY translations.py .
COPY components/ ./components/
COPY assets/ ./assets/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/ || exit 1

ENTRYPOINT ["python", "app.py"]
