FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential gcc g++ libopenblas-dev poppler-utils     && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rag_server.py ./rag_server.py
COPY ingest.py ./ingest.py

EXPOSE 8000
CMD ["uvicorn", "rag_server:app", "--host", "0.0.0.0", "--port", "8000"]
