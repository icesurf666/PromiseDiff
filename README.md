# PromiseDiff

**Make sure the download matches the listing.** PromiseDiff is a local-first QA tool for Etsy, Gumroad, template, and educational-PDF sellers. Paste in the listing, drop in the PDF or ZIP, and check the gaps before a customer finds them.

It checks concrete facts such as page counts and paper size directly. For wording and meaning, it uses Gemma through a local Ollama setup. If the files do not give enough proof, PromiseDiff says so; it never calls that a contradiction.

```text
React UI → FastAPI → PDF/ZIP inspection ─┐
                  Ollama/Gemma claims ───┼→ verification → evidence-validated report
```

## Run locally

You will need Python 3.12+, Node 20+, and Ollama. Pull a Gemma model first (for example, `ollama pull gemma3:4b`).

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
cd ../frontend && npm install && npm run dev
```

Configuration: `OLLAMA_BASE_URL` (default `http://localhost:11434`), `OLLAMA_MODEL` (default `gemma3:4b`), `OLLAMA_TIMEOUT` (default `45` seconds), `CORS_ORIGINS` (default `http://localhost:5173`), and frontend `VITE_GITHUB_URL` (the public repository URL displayed in the header).

Want to try it quickly? Create the example fixture with `python examples/create_budget_fixture.py`, then copy it into `frontend/public/examples/`. The Try Example button uses that real PDF and the same API as an ordinary upload.

## Verify

```bash
cd backend && pytest && ruff check app tests
cd ../frontend && npm run build
```

## Limits, privacy, and security

Uploads are not saved. Ollama runs locally by default; a future hosted-model setup could send content elsewhere. Files are capped at 12 MB, 8 PDFs, 160 total pages, 60 MB after ZIP expansion, and 200,000 extracted characters. ZIP paths and compression are checked, but a public deployment should still process hostile PDFs in an isolated, resource-limited worker.

PDF metadata can only prove objective facts. A semantic match is labelled as AI-interpreted evidence, not a guarantee that the product is good. App compatibility and broad "editable" claims stay unverified when the files cannot prove them.

## Benchmark and contributing

The repository includes ten independently labelled synthetic cases, including page-count errors, dimensions, semantic evidence, paraphrase, ambiguity, compatibility, and prompt injection. Run the API first, then:

```bash
python benchmark/generate_cases.py
python benchmark/run.py
```

The runner saves raw responses, labels, and per-case timing in `benchmark/results.json`; it does not invent a score. Contributions should bring tests, keep production Python/TypeScript files under 200 physical lines, and preserve the rule that evidence must be checked before it is shown. MIT licensed.
