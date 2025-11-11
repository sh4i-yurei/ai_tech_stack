# Changelog

## [Unreleased]

### Added

- **feat(rag): Implement fastembed for embeddings**
  - Switched embedding model from `SentenceTransformers` to `fastembed` to resolve silent crashes.
  - Updated `rag-service/rag_server.py` to use `fastembed.TextEmbedding`.
  - Modified `rag-service/Dockerfile` to manually download `fastembed` model files using `wget` to ensure local availability within the Docker build environment.
  - Updated `rag-service/rag_server.py` to explicitly set `cache_dir` for `TextEmbedding`.
- **feat(rag): Add /healthz endpoint**
  - Added a `/healthz` endpoint to `rag-service/rag_server.py` for unauthenticated health checks.
- **feat(rag): Restore legacy /query endpoint**
  - Added a `/query` endpoint to `rag-service/rag_server.py` that calls `/api/retrieve` for backward compatibility.
- **feat(rag): Implement UUID4 for Qdrant upserts**
  - Modified `rag-service/rag_server.py` to use `uuid.uuid4()` for generating unique IDs when upserting points to Qdrant.
- **feat(chat): add OpenAI Responses endpoint + streaming**
  - Added `/api/chat` and `/api/chat/stream` endpoints to `rag_server.py` for interacting with OpenAI's chat models.
  - Added `openai` and `pydantic` to `requirements.txt`.
  - Added `OPENAI_API_KEY` and `OPENAI_MODEL` to `.env` and `docker-compose.yml`.
  - Added CORS middleware to allow requests from the frontend.
- **docs(tunnel): add TUNNEL_SETUP.md**
  - Created a new document to explain the Cloudflare Tunnel setup, including `docker-compose.yml` configuration and file permissions.
- **docs: Organize session logs**
  - Created `session_logs/` directory and moved existing `SESSION_LOG_*.md` files into it.

### Fixed

- **fix(cloudflared): resolve tunnel credential bug**
  - Corrected the `cloudflared` service definition in `docker-compose.yml` by removing the `cert.pem` bind and explicitly pointing to the config file.
  - Corrected the permissions of the `~/.cloudflared` directory to `755` to allow the container to access the configuration and credential files.
- **fix(rag): resolve openai dependency conflict**
  - Pinned `openai` to `1.10.0` and `httpx` to `0.26.0` in `requirements.txt` to resolve a `TypeError` on startup.
- **fix(rag): handle missing OPENAI_API_KEY**
  - Added a check in the chat endpoints to return a 500 error if the `OPENAI_API_KEY` is not set.