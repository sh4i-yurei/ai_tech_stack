# Changelog

## [Unreleased]

### Added

- **feat(chat): add OpenAI Responses endpoint + streaming**
  - Added `/api/chat` and `/api/chat/stream` endpoints to `rag_server.py` for interacting with OpenAI's chat models.
  - Added `openai` and `pydantic` to `requirements.txt`.
  - Added `OPENAI_API_KEY` and `OPENAI_MODEL` to `.env` and `docker-compose.yml`.
  - Added CORS middleware to allow requests from the frontend.
- **docs(tunnel): add TUNNEL_SETUP.md**
  - Created a new document to explain the Cloudflare Tunnel setup, including `docker-compose.yml` configuration and file permissions.

### Fixed

- **fix(cloudflared): resolve tunnel credential bug**
  - Corrected the `cloudflared` service definition in `docker-compose.yml` by removing the `cert.pem` bind and explicitly pointing to the config file.
  - Corrected the permissions of the `~/.cloudflared` directory to `755` to allow the container to access the configuration and credential files.
- **fix(rag): resolve openai dependency conflict**
  - Pinned `openai` to `1.10.0` and `httpx` to `0.26.0` in `requirements.txt` to resolve a `TypeError` on startup.
- **fix(rag): handle missing OPENAI_API_KEY**
  - Added a check in the chat endpoints to return a 500 error if the `OPENAI_API_KEY` is not set.