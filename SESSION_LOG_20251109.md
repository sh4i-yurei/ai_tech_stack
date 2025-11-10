# Session Log: Agentic AI Stack Build & Troubleshooting (2025-11-09)

**Date:** November 9, 2025
**Objective:** Build and configure the "Agentic AI Stack" locally, including GPU support, and integrate with terminal aliases and n8n.

---

## 🎯 Phase 1: Project Setup & Initial Docker Build

### 1.1 GitHub Repository Creation
- **Goal:** Create a new GitHub repository for the AI stack.
- **Action:** User created `https://github.com/sh4i-yurei/ai_tech_stack`.
- **Description:** "Build a local, reliable AI stack where all assistants (ChatGPT, Gemini CLI, MCP tools) read from the same rules, SOPs, and notes, so answers are consistent and cited."
- **Configuration:** Initialized with README and Python .gitignore.

### 1.2 Local Repository Setup
- **Goal:** Clone the new GitHub repository and prepare the local environment.
- **Action:** Created local directory `~/ai_tech_stack/`.
- **Action:** Initialized Git in `~/ai_tech_stack/`.
- **Action:** Added remote origin: `https://github.com/sh4i-yurei/ai_tech_stack.git`.
- **Action:** Pulled initial files (`README.md`, `.gitignore`) from GitHub.

### 1.3 Phase 0 — Sanity Checks
- **Goal:** Verify Docker installation and free ports.
- **Action:** Executed `docker --version` and `docker compose version`.
- **Outcome:** Docker version 28.5.1, Docker Compose v2.40.2-desktop.1 confirmed working.
- **Action:** Checked ports 8000, 6333, 7700, 5678 using `lsof -i :<port>`.
- **Outcome:** All required ports confirmed FREE.

### 1.4 Initial Stack Deployment (Attempt 1)
- **Goal:** Build and start the AI stack using `docker compose up -d --build`.
- **Action:** Executed `docker compose up -d --build` from `~/`.
- **Outcome:** Failed due to `meilisearch==0.32.3` incompatibility with Python 3.11.

### 1.5 Fix: `meilisearch` Version
- **Goal:** Update `meilisearch` to a compatible version.
- **Action:** Updated `rag-service/requirements.txt` from `meilisearch==0.32.3` to `meilisearch==0.37.1`.
- **Outcome:** `requirements.txt` updated.

---

## 🎯 Phase 2: GPU Integration & Troubleshooting

### 2.1 GPU Capability Check
- **Goal:** Verify Docker's ability to access the NVIDIA GPU.
- **Action:** Executed `docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi`.
- **Outcome:** Confirmed NVIDIA GeForce RTX 3070 detected and accessible within Docker.

### 2.2 GPU Integration (Attempt 1)
- **Goal:** Configure Docker for GPU support.
- **Action:** Modified `rag-service/Dockerfile`:
    - Changed base image to `nvidia/cuda:12.1.0-base-ubuntu22.04`.
- **Action:** Modified `docker-compose.yml`:
    - Added `deploy.resources.reservations.devices` to `rag` service.
- **Action:** Executed `docker compose up -d --build`.
- **Outcome:** Failed with `/bin/sh: 1: pip: not found`.

### 2.3 Fix: Install `pip` in CUDA Image
- **Goal:** Ensure `pip` is available in the CUDA base image.
- **Action:** Modified `rag-service/Dockerfile`:
    - Added `RUN apt-get update && apt-get install -y python3-pip`.
- **Action:** Executed `docker compose up -d --build`.
- **Outcome:** Failed with `double free detected in tcache 2` and `NumPy` incompatibility warning.

### 2.4 Fix: `torch` Version & `NumPy` Incompatibility
- **Goal:** Resolve low-level `double free` and `NumPy` issues.
- **Action:** Modified `rag-service/Dockerfile`:
    - Changed base image to `nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04` (newer, non-deprecated).
    - Updated `torch` installation command to `RUN pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cu121`.
- **Action:** Modified `rag-service/requirements.txt`:
    - Added `numpy==1.26.4` to explicitly pin a compatible version.
- **Action:** Executed `docker compose up -d --build --force-recreate`.
- **Outcome:** Failed with `torch==2.3.1` not found for `cu123`.

### 2.5 Fix: Correct `torch` Installation for CUDA 12.8
- **Goal:** Install correct `torch` version for CUDA 12.8.
- **Action:** Modified `rag-service/Dockerfile`:
    - Changed `torch` installation command to `RUN pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cu121`. (This was a re-attempt with a known stable version).
- **Action:** Executed `docker compose up -d --build --force-recreate`.
- **Outcome:** Failed with `double free detected in tcache 2` again.

### 2.6 Revert to CPU-Only (Pragmatic Approach)
- **Goal:** Get the core RAG stack working reliably on CPU, then re-attempt GPU integration.
- **Action:** Modified `rag-service/Dockerfile`:
    - Changed base image back to `python:3.11-slim`.
    - Removed `RUN apt-get update && apt-get install -y python3-pip`.
    - Removed `RUN pip install torch...` line.
- **Action:** Modified `docker-compose.yml`:
    - Removed `deploy` section from `rag` service.
- **Action:** Modified `rag-service/.env`:
    - Removed `CUDA_VISIBLE_DEVICES=""`.
- **Action:** Executed `docker compose up -d --build --force-recreate`.
- **Outcome:** Build successful.

---

## 🎯 Phase 3: Port Conflicts & Final Stack Deployment

### 3.1 Port Conflict: `postgres` (5432)
- **Goal:** Resolve port conflict for `postgres`.
- **Action:** Modified `docker-compose.yml`:
    - Changed `postgres` host port from `5432:5432` to `5433:5432`.
- **Action:** Executed `docker compose up -d --build`.
- **Outcome:** Failed with `redis` port conflict.

### 3.2 Port Conflict: `redis` (6379)
- **Goal:** Resolve port conflict for `redis`.
- **Action:** Modified `docker-compose.yml`:
    - Changed `redis` host port from `6379:6379` to `6380:6379`.
- **Action:** Executed `docker compose up -d --build`.
- **Outcome:** Failed with `meilisearch` port conflict.

### 3.3 Port Conflict: `meilisearch` (7700)
- **Goal:** Resolve port conflict for `meilisearch`.
- **Action:** Modified `docker-compose.yml`:
    - Changed `meilisearch` host port from `7700:7700` to `7701:7700`.
- **Action:** Executed `docker compose up -d --build`.
- **Outcome:** Failed with `n8n` port conflict.

### 3.4 Port Conflict: `n8n` (5678)
- **Goal:** Resolve port conflict for `n8n`.
- **Action:** Modified `docker-compose.yml`:
    - Changed `n8n` host port from `5678:5678` to `5679:5678`.
- **Action:** Executed `docker compose up -d --build`.
- **Outcome:** All services started successfully.

### 3.5 Health Check
- **Goal:** Verify RAG API is running.
- **Action:** Executed `curl -s http://localhost:8000/health`.
- **Outcome:** `{"status":"ok", ...}` confirmed.

---

## 🎯 Phase 4: Knowledge Ingestion & Query Verification

### 4.1 Put Knowledge in Place
- **Goal:** Add sample knowledge files.
- **Action:** Created `knowledge/rules/00_operating_rules.md`.
- **Action:** Created `knowledge/sop/ubuntu_patch.md`.
- **Action:** Copied `~/sec_blog-resume/DOCUMENTATION_GUIDE.md` to `knowledge/rules/`.

### 4.2 Ingest Knowledge
- **Goal:** Index knowledge files into the RAG API.
- **Action:** Executed `curl -X POST http://localhost:8000/ingest -H 'Content-Type: application/json' -d '{"path":"knowledge","namespace":"main"}'`.
- **Outcome:** `{"ingested_files":4,"chunks":7,"namespace":"main"}` confirmed successful ingestion.

### 4.3 Ask a Question & Verify Sources
- **Goal:** Test RAG API query and source citation.
- **Action:** Executed `curl -X POST http://localhost:8000/query -H 'Content-Type: application/json' -d '{"query":"Show Ubuntu patch steps","namespace":"main","k":6,"hybrid":true}'`.
- **Outcome:** Received a JSON response with `answer`, `context`, and `matches` citing `knowledge/sop/ubuntu_patch.md` and `knowledge/rules/DOCUMENTATION_GUIDE.md`.

---

## 🎯 Phase 5: Tool Integration

### 5.1 Terminal Aliases
- **Goal:** Create quick access aliases for RAG tools in the terminal.
- **Action:** Appended `raging`, `rags`, `raga` aliases to `~/.bashrc`.
- **Action:** User ran `source ~/.bashrc`.
- **Action:** User tested `raging`, `rags "operating rules"`, `raga "show ubuntu patch steps"`.
- **Outcome:** All aliases confirmed working, returning JSON responses.

### 5.2 VS Code MCP Integration (Troubleshooting)
- **Goal:** Integrate RAG tools with VS Code via MCP extension.
- **Action:** User installed "VS Code MCP Server" extension by `juehang`.
- **Action:** User updated Windows-side `settings.json` with `mcp.servers` configuration (using absolute WSL paths).
- **Outcome:** Integration pending successful testing in VS Code.

---

## ✅ Session Conclusion

This session successfully built and configured the "Agentic AI Stack" in a CPU-only Docker environment, resolved numerous build and port conflicts, and verified the core RAG API functionality. Terminal aliases for RAG tools are fully operational. Integration with VS Code via the MCP extension is configured, pending final verification of the VS Code UI interaction.
