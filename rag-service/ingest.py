import os, argparse, requests, json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="knowledge", help="folder to ingest")
    ap.add_argument("--namespace", default=os.environ.get("NAMESPACE","main"))
    ap.add_argument("--host", default="http://localhost:8000")
    args = ap.parse_args()
    payload = {"path": args.path, "namespace": args.namespace}
    r = requests.post(f"{args.host}/ingest", json=payload, timeout=600)
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    main()
