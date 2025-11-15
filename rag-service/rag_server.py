import os, glob, uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# ---- Embedder (fast, no torch) ----
from fastembed import TextEmbedding

app = FastAPI(title="RAG Service")

# CORS stays as you already configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://rag.keepbreath.ing"],
    allow_methods=["POST","GET","OPTIONS"],
    allow_headers=["*"],
)

# ---- Bearer gate (you already added this) ----
RAG_ACTION_KEY = os.getenv("RAG_ACTION_KEY","")
@app.middleware("http")
async def require_action_key(request: Request, call_next):
    if request.url.path.startswith("/health"):
        return await call_next(request)
    auth = request.headers.get("authorization", "")
    if RAG_ACTION_KEY and not (auth.startswith("Bearer ") and auth.split(" ",1)[1] == RAG_ACTION_KEY):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)

# ---- Models for retrieve ----
class RetrieveIn(BaseModel):
    query: str
    top_k: Optional[int] = None

class Chunk(BaseModel):
    id: str
    score: float
    text: str
    source: Optional[str] = None

class RetrieveOut(BaseModel):
    chunks: List[Chunk]

class IngestIn(BaseModel):
    path: str = "/app/knowledge"  # container path

# ---- Clients / config ----
_QDRANT_URL = os.getenv("QDRANT_URL","http://qdrant:6333")
_COLLECTION = os.getenv("QDRANT_COLLECTION","docs")
_TOPK_DEFAULT = int(os.getenv("RETRIEVE_TOPK","5"))

_qc = QdrantClient(_QDRANT_URL)
# bge-small-en-v1.5 → 384-dim (same width as MiniLM), fast & container-safe
_embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5", cache_dir=".cache/fastembed")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/api/retrieve", response_model=RetrieveOut)
def retrieve(in_: RetrieveIn):
    # 1) embed query (fastembed yields a generator)
    try:
        qvec = next(_embedder.embed([in_.query]))
    except Exception:
        # if embedding ever failed, return empty instead of crashing
        return RetrieveOut(chunks=[])

    # 2) search qdrant
    k = in_.top_k or _TOPK_DEFAULT
    try:
        res = _qc.search(
            collection_name=_COLLECTION,
            query_vector=list(qvec),
            limit=k,
            with_payload=True,
            with_vectors=False,
        )
    except Exception:
        return RetrieveOut(chunks=[])

    # 3) shape response
    out = []
    for r in res:
        p = r.payload or {}
        out.append(Chunk(
            id=str(r.id),
            score=float(r.score),
            text=p.get("text",""),
            source=p.get("source"),
        ))
    return RetrieveOut(chunks=out)

@app.post("/query", response_model=RetrieveOut)
def query(in_: RetrieveIn):
    return retrieve(in_)

@app.post("/ingest")
def ingest(in_: IngestIn):
    def _collect_files(base_dir: str) -> list:
        if not os.path.exists(base_dir):
            return []
        gathered = []
        for walk_dir, _, _ in os.walk(base_dir):
            for ext in ("*.md", "*.txt", "*.json"):
                gathered.extend(glob.glob(os.path.join(walk_dir, ext)))
        return gathered

    root = os.path.abspath(in_.path)
    files = _collect_files(root)
    if not files and root.startswith("/app/"):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        alt_root = os.path.join(repo_root, root[len("/app/"):])
        files = _collect_files(alt_root)
        if files:
            root = alt_root
    if not files:
        raise HTTPException(status_code=400, detail=f"No files found under {root}")

    texts, payloads = [], []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                t = f.read().strip()
        except Exception:
            continue
        if not t:
            continue
        texts.append(t)
        payloads.append({"text": t, "source": os.path.basename(fp)})

    if not texts:
        raise HTTPException(status_code=400, detail="No non-empty docs")

    # Embed and upsert
    emb = TextEmbedding(model_name="BAAI/bge-small-en-v1.5", cache_dir=".cache/fastembed")
    vecs = list(emb.embed(texts))

    qc = QdrantClient(url=os.getenv("QDRANT_URL", "http://qdrant:6333"))
    COL = os.getenv("QDRANT_COLLECTION", "docs")
    try:
        qc.get_collection(COL)
    except Exception:
        qc.recreate_collection(
            COL,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    points = [PointStruct(id=str(uuid.uuid4()), vector=vecs[i], payload=payloads[i]) for i in range(len(texts))]
    qc.upsert(collection_name=COL, points=points)
    return {"ingested": len(points), "collection": COL}
