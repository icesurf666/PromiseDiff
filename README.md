# PromiseDiff

**Verify what you promise before you sell.** PromiseDiff is a local-first QA tool for Etsy, Gumroad, template, and educational-PDF sellers. Paste a listing, upload its PDF or ZIP deliverable, and inspect evidence-backed differences before publishing.

It measures facts such as PDF page counts and paper dimensions deterministically, then uses a locally configured Gemma model through Ollama for claim extraction and evidence-aware semantic matching. Missing evidence is never treated as a contradiction.

```text
React UI → FastAPI → PDF/ZIP inspection ─┐
                  Ollama/Gemma claims ───┼→ verification → evidence-validated report
```

## Run locally

Requires Python 3.12+, Node 20+, and Ollama. Install and start a Gemma model available on your installation (for example `ollama pull gemma3:4b`).

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
cd ../frontend && npm install && npm run dev
```

Configuration: `OLLAMA_BASE_URL` (default `http://localhost:11434`), `OLLAMA_MODEL` (default `gemma3:4b`), `OLLAMA_TIMEOUT` (default `45` seconds), and `CORS_ORIGINS` (default `http://localhost:5173`).

Create the example fixture with `python examples/create_budget_fixture.py`, then copy it into `frontend/public/examples/`. The Try Example button uses that actual PDF and the regular analysis endpoint.

## Verify

```bash
cd backend && pytest && ruff check app tests
cd ../frontend && npm run build
```

## Limits, privacy, and security

Uploads are not persisted. Local Ollama is the default; a future hosted inference setup could send content externally. Inputs are limited to 12 MB, 8 PDFs, 160 total pages, 60 MB decompressed ZIP data, and 200,000 extracted characters. ZIP paths and compression are checked, but hostile PDFs should be processed in resource-limited isolation in public deployments.

PDF metadata can verify only objective facts. Semantic support is explicitly AI-interpreted evidence, not a guarantee of content quality. Compatibility claims and general editability are deliberately out of scope or unverified when untestable.

## Benchmark and contributing

The repository includes ten independently labelled synthetic cases, including page-count errors, dimensions, semantic evidence, paraphrase, ambiguity, compatibility, and prompt injection. Run the API first, then:

```bash
python benchmark/generate_cases.py
python benchmark/run.py
```

The runner records raw responses, status labels, and per-case latency in `benchmark/results.json`; it does not fabricate metrics. Contributions should include tests, keep production Python/TypeScript files under 200 physical lines, and preserve the evidence-validation invariant. MIT licensed.
