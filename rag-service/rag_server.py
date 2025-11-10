import os, io, re, uuid, glob, json, time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Response
from pydantic import BaseModel
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from rank_bm25 import BM25Okapi
import numpy as np
from prometheus_client import Counter, Gauge, generate_latest

try:
    import meilisearch
except Exception:
    meilisearch = None

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
MEILI_URL = os.getenv("MEILI_URL", "http://localhost:7700")
EMB_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

app = FastAPI(title="Enterprise RAG API")

Q_QUERIES = Counter("rag_queries_total", "Total /query calls")
Q_INGEST = Counter("rag_ingest_total", "Total /ingest calls")
G_VECTORS = Gauge("rag_vectors", "Vectors per namespace", ["namespace"])

try:
    print(f"Loading SentenceTransformer model: {EMB_MODEL_NAME}")
    _model = SentenceTransformer(EMB_MODEL_NAME)
    print(f"SentenceTransformer model loaded successfully. Vector dim: {_model.get_sentence_embedding_dimension()}")
except Exception as e:
    print(f"ERROR: Failed to load SentenceTransformer model: {e}")
    raise # Re-raise the exception to ensure container crashes if it's a fatal error

VECTOR_DIM = _model.get_sentence_embedding_dimension()
def embed(texts: List[str]):
    return _model.encode(texts, normalize_embeddings=True)

qc = QdrantClient(url=QDRANT_URL)
ms = None
if meilisearch:
    try:
        ms = meilisearch.Client(MEILI_URL)
    except Exception:
        ms = None

def ensure_collection(name: str):
    try:
        qc.get_collection(name)
    except Exception:
        qc.create_collection(
            collection_name=name,
            vectors_config=qm.VectorParams(size=VECTOR_DIM, distance=qm.Distance.COSINE),
        )

def load_text_from_path(path: str) -> List[Dict[str, Any]]:
    out = []
    for fp in glob.glob(os.path.join(path, "**"), recursive=True):
        if os.path.isdir(fp):
            continue
        ext = os.path.splitext(fp)[1].lower()
        try:
            if ext in [".md", ".txt"]:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    out.append({"text": f.read(), "source": fp})
            elif ext in [".pdf"]:
                reader = PdfReader(fp)
                buf = []
                for page in reader.pages:
                    try:
                        buf.append(page.extract_text() or "")
                    except Exception:
                        pass
                out.append({"text": "\n".join(buf), "source": fp})
        except Exception as e:
            print(f"[WARN] reading {fp}: {e}")
    return out

def simple_chunk(text: str, max_chars=1200, overlap=200) -> List[str]:
    text = re.sub(r"\s+"," ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
        if end == len(text):
            break
    return chunks

_bm25_index: Dict[str, Dict[str, Any]] = {}
def rebuild_bm25(namespace: str, texts: List[str]):
    tokenized = [t.lower().split() for t in texts]
    _bm25_index[namespace] = {
        "bm25": BM25Okapi(tokenized) if texts else None,
        "texts": texts,
    }

class IngestReq(BaseModel):
    path: str
    namespace: str = "main"

class QueryReq(BaseModel):
    query: str
    namespace: str = "main"
    k: int = 6
    hybrid: bool = True
    return_context_only: bool = False

@app.get("/health")
def health():
    return {"status":"ok","qdrant":QDRANT_URL,"meili":bool(ms),"model":EMB_MODEL_NAME,"dim":VECTOR_DIM}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.post("/ingest")
def ingest(req: IngestReq):
    Q_INGEST.inc()
    ns = req.namespace
    ensure_collection(ns)

    raw_docs = load_text_from_path(req.path)
    total_chunks = 0
    plain_texts = []

    points = []
    if ms:
        try:
            ms.index(ns).get_raw_info()
        except Exception:
            ms.create_index(uid=ns, options={"primaryKey": "id"})

    for doc in raw_docs:
        chunks = simple_chunk(doc["text"])
        total_chunks += len(chunks)
        plain_texts.extend(chunks)
        for ch in chunks:
            points.append({
                "id": str(uuid.uuid4()),
                "payload": {"text": ch, "source": doc["source"], "namespace": ns},
            })

    batch = 64
    vecs = []
    for i in range(0, len(points), batch):
        texts = [p["payload"]["text"] for p in points[i:i+batch]]
        vecs.extend(embed(texts))

    if points:
        qc.upsert(
            collection_name=ns,
            points=qm.Batch(
                ids=[p["id"] for p in points],
                vectors=vecs,
                payloads=[p["payload"] for p in points],
            ),
        )
        collection_info = qc.get_collection(ns)
        vectors_count = collection_info.vectors_count if collection_info.vectors_count is not None else 0
        G_VECTORS.labels(ns).set(vectors_count)

        if ms:
            docs = [{"id": p["id"], "text": p["payload"]["text"], "source": p["payload"]["source"]} for p in points]
            ms.index(ns).add_documents(docs)

    rebuild_bm25(ns, plain_texts)
    return {"ingested_files": len(raw_docs), "chunks": total_chunks, "namespace": ns}

def qdrant_search(namespace: str, query: str, k: int):
    ensure_collection(namespace)
    qvec = embed([query])[0]
    res = qc.search(
        collection_name=namespace,
        query_vector=qvec,
        limit=k,
        with_payload=True,
        score_threshold=None
    )
    matches = []
    for r in res:
        pl = r.payload or {}
        matches.append({
            "score": float(r.score),
            "text": pl.get("text",""),
            "source": pl.get("source",""),
            "namespace": pl.get("namespace", namespace),
        })
    return matches

def bm25_search(namespace: str, query: str, k: int):
    idx = _bm25_index.get(namespace)
    if not idx or not idx.get("bm25"):
        return []
    tokenized = query.lower().split()
    scores = idx["bm25"].get_scores(tokenized)
    pairs = list(enumerate(scores))
    pairs.sort(key=lambda x: x[1], reverse=True)
    texts = idx["texts"]
    out = []
    for (i, s) in pairs[:k]:
        out.append({"score": float(s), "text": texts[i], "source": "bm25", "namespace": namespace})
    return out

def meili_search(namespace: str, query: str, k: int):
    if not ms:
        return []
    try:
        hits = ms.index(namespace).search(query, {"limit": k}).get("hits", [])
        out = []
        for h in hits:
            out.append({"score": 1.0, "text": h.get("text",""), "source": h.get("source",""), "namespace": namespace})
        return out
    except Exception:
        return []

def synthesize_answer(query: str, snippets: List[str], max_chars=1200) -> str:
    joined = "\n- " + "\n - ".join([s[:300] for s in snippets])
    return f"Context bullets (extracts):{joined}\n\nUser question: {query}\n\nUse the context bullets above to answer precisely and cite sources."

@app.post("/query")
def query(req: QueryReq):
    Q_QUERIES.inc()
    vres = qdrant_search(req.namespace, req.query, req.k)
    lres = bm25_search(req.namespace, req.query, req.k)
    mres = meili_search(req.namespace, req.query, req.k)

    combined = vres + mres + lres if req.hybrid else vres
    seen = set()
    fused = []
    for m in combined:
        key = (m["text"], m.get("source",""))
        if key in seen:
            continue
        seen.add(key)
        fused.append(m)
    matches = fused[:req.k]

    snippets = [m["text"] for m in matches]
    context = "\n\n---\n".join([f"{m['text']}\n(Source: {m['source']})" for m in matches])
    if req.return_context_only:
        return {"context": context, "matches": matches}

    answer = synthesize_answer(req.query, snippets)
    return {"answer": answer, "context": context, "matches": matches}

@app.get("/diag/index")
def diag_index():
    colls = qc.get_collections().collections
    out = {}
    for c in colls:
        name = c.name
        info = qc.get_collection(name)
        out[name] = {
            "vectors_count": info.vectors_count,
            "status": str(info.status),
        }
    return out
