"""Run sample queries and check the answers.

For each query: either the answer must contain one of the expected keywords,
or the help desk must fall back to the escalation message.

Run: python -m tests.run_eval   (build the index first: python -m scripts.ingest)
Add more queries to tests/queries.json to grow coverage.
"""
import json
from pathlib import Path

from app.rag.chain import HelpDesk

QUERIES = json.loads((Path(__file__).parent / "queries.json").read_text())


def main():
    desk = HelpDesk()
    passed = 0
    for q in QUERIES:
        result = desk.ask(q["query"])
        if q["expect_fallback"]:
            ok = result["fallback"]
        else:
            ok = (not result["fallback"]) and any(k.lower() in result["answer"].lower() for k in q["expect_any"])
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {q['id']}: {q['query']}")
    print(f"\n{passed}/{len(QUERIES)} queries passed")


if __name__ == "__main__":
    main()
