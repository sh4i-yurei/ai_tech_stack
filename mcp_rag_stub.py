#!/usr/bin/env python3
"""
MCP stdio stub that forwards to the local RAG HTTP API.
Tools:
- rag.search
- rag.ask
- rag.ingest
"""
import sys, json, os, requests

RAG_URL = os.environ.get("RAG_URL", "http://localhost:8000")

def handle_call(req):
    mid = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    try:
        if method == "rag.search":
            q = params.get("query","")
            ns = params.get("namespace","main")
            k = int(params.get("k", 5))
            r = requests.post(f"{RAG_URL}/query", json={"query": q, "namespace": ns, "k": k, "hybrid": True, "return_context_only": True}, timeout=120)
            data = r.json()
            return {"jsonrpc":"2.0","id":mid,"result":data}

        if method == "rag.ask":
            q = params.get("query","")
            ns = params.get("namespace","main")
            k = int(params.get("k", 6))
            r = requests.post(f"{RAG_URL}/query", json={"query": q, "namespace": ns, "k": k, "hybrid": True}, timeout=120)
            data = r.json()
            return {"jsonrpc":"2.0","id":mid,"result":data}

        if method == "rag.ingest":
            path = params.get("path","knowledge")
            ns = params.get("namespace","main")
            r = requests.post(f"{RAG_URL}/ingest", json={"path": path, "namespace": ns}, timeout=600)
            data = r.json()
            return {"jsonrpc":"2.0","id":mid,"result":data}

        return {"jsonrpc":"2.0","id":mid,"error":{"code":-32601,"message":"Method not found"}}
    except Exception as e:
        return {"jsonrpc":"2.0","id":mid,"error":{"code":-32000,"message":str(e)}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        resp = handle_call(req)
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
