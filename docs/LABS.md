# Labs — Step by Step (Plain Language)

## Before you start
- Windows 11 + WSL 2 + Docker Desktop running.
- In WSL terminal: `docker --version` works.

## Lab 1 — Core stack up (RAG + Qdrant)
1) Go to the project folder:
```bash
cd ~/enterprise-ai-stack
docker compose up -d --build
```
2) Health check:
```bash
curl -s http://localhost:8000/health
```
Expected: JSON with `"status":"ok"`.
3) Ingest:
```bash
curl -X POST http://localhost:8000/ingest -H 'Content-Type: application/json' -d '{"path":"knowledge","namespace":"main"}'
```
4) Query:
```bash
curl -X POST http://localhost:8000/query -H 'Content-Type: application/json' -d '{"query":"Show Ubuntu patch steps","namespace":"main","k":6,"hybrid":true}'
```

## Lab 2 — Hybrid retrieval with Meilisearch
- Meilisearch starts automatically. Hybrid is on when you pass `"hybrid": true`.
- Try exact-term queries and confirm results still look good.

## Lab 3 — Auto-ingest with n8n
1) Open http://localhost:5678 and finish setup.
2) Import `orchestrator/n8n/flows.json` → activate the workflow.
3) It runs hourly. Click **Execute** to test now (expect HTTP 200).

## Lab 4 — MCP usage
- Use your MCP-capable client and add a local server that runs:
```
python3 mcp_rag_stub.py   (with env RAG_URL=http://localhost:8000)
```
- Tools: `rag.search`, `rag.ask`, `rag.ingest`

## Lab 5 — Agent basics
1) Run:
```bash
python3 agents/ops_agent.py "Patch Ubuntu per SOP"
```
2) See a safe plan (read-only) with sources.

## Lab 6 — Logging & evaluation
- Metrics: `curl -s http://localhost:8000/metrics`
- Create 5–10 test questions in a file, compare whether expected files appear in top-3 matches.

## Lab 7 — Security quick wins
- Keep the API on localhost.
- Use PRs to review changes in `knowledge/`.
- Don’t commit secrets. Use `.env` files that are ignored by Git.
