# Enterprise Agentic AI Stack — Starter (WSL-friendly)

This project teaches you step by step. You will **build** and **use** an agentic AI stack on your PC. 
It is simple first, then grows.

## What you get
- RAG API (FastAPI) + Qdrant (vectors) + Meilisearch (keywords)
- n8n orchestrator (HTTP flows that call your RAG API)
- MCP stub so MCP-aware apps can call your RAG API as tools
- A minimal agent script that plans with your rules/SOPs (no external API keys required)
- Lab docs in `/docs` with exact steps

## Labs (do in order)
1. Core stack up (RAG + Qdrant) — 15 min
2. Add Meilisearch (hybrid retrieval) — 10 min
3. Auto-ingest with n8n (cron → HTTP request) — 15 min
4. Use from MCP clients — 10 min
5. Agent basics (small planner script) — 10 min
6. Logging & evaluation basics — 10 min
7. Security sanity checklist — 10 min

Open `docs/LABS.md` and start with **Lab 1**.
