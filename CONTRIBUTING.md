# Contributing to PromiseDiff

Thanks for helping make product listings a little less surprising for buyers.

## Before opening a pull request

1. Keep the change focused and explain the user-facing behaviour it changes.
2. Add or update tests for backend behaviour and frontend states where relevant.
3. Run the checks below from the repository root:

```bash
cd backend && source .venv/bin/activate
pytest -q
ruff check app tests
cd ../frontend && npm test -- --run && npm run build
```

## A few project rules

- Never mark a claim contradicted merely because there is no evidence for it.
- Any semantic support needs a filename, page number, and exact quote that the backend validates.
- Treat PDFs and ZIPs as untrusted input. Keep limits and archive checks intact.
- Keep production Python, TypeScript, and TSX files below 200 physical lines.
- Do not add uploads, listings, or customer content to fixtures or commits.

## Good first contributions

- Fixtures for a missing PDF or ZIP edge case.
- Better retrieval for semantic paraphrases.
- Clearer error states and accessibility improvements.
- Benchmark cases with an independently assigned gold label.
