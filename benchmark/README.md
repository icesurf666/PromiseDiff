# Reproducible benchmark scaffold

`cases.json` contains independently assigned synthetic gold labels. Generate inputs then run against the normal local API:

```bash
python benchmark/generate_cases.py
python benchmark/run.py
```

The runner writes raw API responses, final classifications, and latency to `results.json`; it never fabricates metrics. A direct-model baseline can be added with the same fixtures and recorded beside this output.
