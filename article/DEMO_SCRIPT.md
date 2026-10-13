# PromiseDiff demo script

1. Open the local app and say: “PromiseDiff checks that digital-product listings match the files a customer downloads.”
2. Click **Try Example**. Show the real 48-page PDF name and prefilled listing.
3. Click **Verify Product**. Do not narrate fake progress; say Gemma is evaluating locally through Ollama.
4. Point to the deterministic result: exact page count is supported with metadata evidence.
5. Point to the contradiction: A4 exists, US Letter does not, so the listing claim fails.
6. Expand a semantic finding and show filename, page number, quote, and the `AI-interpreted` label.
7. Export the Markdown report.
8. End with: “It does not claim missing text proves a product is wrong. It returns unverified when it cannot establish the claim.”
