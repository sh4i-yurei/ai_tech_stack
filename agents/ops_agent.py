#!/usr/bin/env python3
import sys, json, requests

RAG_URL = "http://localhost:8000"

def fetch_context(q, ns="main", k=6):
    r = requests.post(f"{RAG_URL}/query", json={
        "query": q, "namespace": ns, "k": k, "hybrid": True, "return_context_only": True
    }, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data.get("matches", [])

def make_plan(goal, matches):
    bullets = [m["text"].strip().splitlines()[0][:120] for m in matches]
    sources = [m["source"] for m in matches]
    plan = ["Goal: " + goal, "", "Plan (read-only):"]
    sop_steps = []
    for m in matches:
        if "SOP" in m["text"] or "sudo apt" in m["text"]:
            sop_steps.extend([s for s in m["text"].splitlines() if s.strip().startswith(("1)","2)","3)","4)","5)"))])
    if sop_steps:
        plan += sop_steps
    else:
        plan += [f"- Review: {b}" for b in bullets[:5]]
    plan += ["", "Sources:"] + [f"- {s}" for s in sources]
    return "\n".join(plan)

def main():
    if len(sys.argv) < 2:
        print("Usage: ops_agent.py "your goal"")
        sys.exit(1)
    goal = sys.argv[1]
    matches = fetch_context(goal)
    print(make_plan(goal, matches))

if __name__ == "__main__":
    main()
