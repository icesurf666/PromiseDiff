"""Generate deterministic PDF inputs for the local benchmark."""
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).parent
CASES = json.loads((ROOT / "cases.json").read_text())
OUTPUT = ROOT / "fixtures"


def build(case: dict[str, object]) -> None:
    document = fitz.open()
    for number in range(int(case["pages"])):
        page = document.new_page(width=595.28, height=841.89)
        page.insert_text((72, 90), str(case["text"]), fontsize=18)
        page.insert_text((72, 130), f"Synthetic benchmark page {number + 1}", fontsize=10)
    document.save(OUTPUT / f"{case['id']}.pdf")


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    for case in CASES:
        build(case)
    print(f"Generated {len(CASES)} fixtures in {OUTPUT}")


if __name__ == "__main__":
    main()
