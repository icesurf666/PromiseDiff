"""Run PromiseDiff cases against a local API and retain raw evidence."""
import json
import os
import time
from collections import Counter
from pathlib import Path

import httpx

ROOT = Path(__file__).parent
API_URL = os.getenv("PROMISEDIFF_API_URL", "http://127.0.0.1:8000/api/analyze")
CASES = json.loads((ROOT / "cases.json").read_text())


def run_case(client: httpx.Client, case: dict[str, object]) -> dict[str, object]:
    path = ROOT / "fixtures" / f"{case['id']}.pdf"
    started = time.perf_counter()
    with path.open("rb") as file:
        response = client.post(API_URL, data={"description": case["description"]}, files={"file": (path.name, file, "application/pdf")})
    elapsed = round((time.perf_counter() - started) * 1000, 1)
    try:
        body = response.json()
    except ValueError:
        body = {"detail": response.text[:500]}
    actual = body.get("findings", [{}])[0].get("status") if response.is_success else None
    return {"id": case["id"], "gold": case["gold"], "actual": actual, "latency_ms": elapsed, "http_status": response.status_code, "raw": body}


def main() -> None:
    if not (ROOT / "fixtures").exists():
        raise SystemExit("Run: python benchmark/generate_cases.py")
    with httpx.Client(timeout=90) as client:
        results = [run_case(client, case) for case in CASES]
    correct = sum(item["gold"] == item["actual"] for item in results)
    report = {"api_url": API_URL, "cases": results, "accuracy": correct / len(results), "status_counts": Counter(item["actual"] for item in results)}
    output = ROOT / "results.json"
    output.write_text(json.dumps(report, indent=2, default=dict))
    print(f"{correct}/{len(results)} exact labels; raw results: {output}")


if __name__ == "__main__":
    main()
