import os, argparse, requests, json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="knowledge", help="folder to ingest")
    ap.add_argument("--namespace", default=os.environ.get("NAMESPACE","main"))
    ap.add_argument("--host", default="http://rag:8000")
    ap.add_argument("--rag-action-key", default=os.environ.get("RAG_ACTION_KEY"))
    args = ap.parse_args()
    payload = {"path": args.path, "namespace": args.namespace}
    headers = {}
    if args.rag_action_key:
        headers["Authorization"] = f"Bearer {args.rag_action_key}"
    r = requests.post(f"{args.host}/ingest", json=payload, headers=headers, timeout=600)
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    main()
