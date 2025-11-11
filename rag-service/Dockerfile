FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential gcc g++ libopenblas-dev poppler-utils git wget     && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV FASTEMBED_CACHE_PATH=/app/.fastembed_cache
RUN mkdir -p ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/model.safetensors && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/pytorch_model.bin && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/config.json && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/tokenizer.json && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/vocab.txt && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/special_tokens_map.json && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/tokenizer_config.json && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/modules.json && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/config_sentence_transformers.json && \
    wget -P ${FASTEMBED_CACHE_PATH}/BAAI/bge-small-en-v1.5 https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/sentence_bert_config.json

COPY rag_server.py ./rag_server.py
COPY ingest.py ./ingest.py

EXPOSE 8000
CMD ["uvicorn", "rag_server:app", "--host", "0.0.0.0", "--port", "8000"]
