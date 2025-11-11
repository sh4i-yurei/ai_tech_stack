# Repository Guidelines

## Project Structure & Module Organization
- `rag-service/`: FastAPI RAG API (ingest + retrieve) plus container assets; edit `requirements.txt` when Python deps change.
- `knowledge/`: Curated sources grouped under `kb/`, `sop/`, `rules/`, plus `quick_smoke.md` for sanity prompts; ingestion mounts this tree read-only inside the rag container.
- `agents/ops_agent.py`: Example autonomous agent that drives orchestrations by calling the RAG API and MCP tools.
- `orchestrator/n8n/`: Self-hosted n8n workspace (flows, binaryData, ssh keys); treat as stateful volume.
- Top-level `docker-compose.yml`, `rag_actions.yaml`, and `mcp_rag_stub.py` describe how local services and Model Context Protocol clients talk to each other.

## Build, Test, and Development Commands
```
docker compose up -d qdrant meilisearch postgres redis n8n rag   # full stack
docker compose logs -f rag                                      # tail FastAPI traces
python -m uvicorn rag_server:app --app-dir rag-service --reload # run service without Docker
python rag-service/ingest.py --path knowledge/kb --host http://localhost:8010 \
  --rag-action-key "$RAG_ACTION_KEY"                            # push docs into Qdrant
npm run release                                                 # bump version via standard-version
```

## Coding Style & Naming Conventions
- Python: 4-space indents, `black`-compatible line widths (88 chars), snake_case functions, PascalCase models, and type hints on FastAPI routes. Keep environment switches (e.g., `RAG_ACTION_KEY`) in `UPPER_SNAKE`.
- YAML/JSON: Two-space indents, keys sorted logically (ports, env, volumes) to ease diffs.
- Markdown: Use level-2 headings per SOP; favor short sentences and actionable steps.

## Testing Guidelines
- Add `pytest` suites under `rag-service/tests/` mirroring module paths; run with `pytest -q rag-service/tests`.
- Smoke-test endpoints manually: `curl -H "Authorization: Bearer $RAG_ACTION_KEY" :8010/api/retrieve`.
- Before ingesting new knowledge, run `python rag-service/ingest.py --path knowledge/quick_smoke.md` to verify embeddings succeed.
- Capture coverage expectations in PRs (target >80% for new Python modules) and document manual steps in `SESSION_LOG_*.md`.

## Commit & Pull Request Guidelines
- Use Conventional Commits (`type(scope): summary`) as seen in history (`docs: …`, `RAG: …`, `chore(release): …`); scope can be directory names (`rag-service`, `agents`).
- Commits should bundle one logical change (code + docs/tests).
- PRs must include: purpose, key commands run, screenshots or log excerpts for orchestration/UI changes, and linked GitHub issues.

## Security & Configuration Tips
- Keep secrets in `.env` (not tracked); export `OPENAI_API_KEY`, `RAG_ACTION_KEY`, `OPENAI_MODEL` before running the stack.
- Cloudflared inherits configs from `/home/mark/.cloudflared`; never commit tunnel creds or n8n SSH material.
- Validate new knowledge files for PII before ingesting, and prefer redacted SOP versions when possible.
