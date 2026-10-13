"""Create the real 48-page A4 fixture used by the example workflow."""
from pathlib import Path
import fitz

OUT = Path(__file__).with_name("budget_planner_A4.pdf")
document = fitz.open()
for index in range(48):
    page = document.new_page(width=595.28, height=841.89)
    heading = "Monthly Budget Review Worksheet" if index % 2 == 0 else "Savings Goal Tracker"
    page.insert_text((72, 88), "2026 BUDGET PLANNER", fontsize=18)
    page.insert_text((72, 135), heading, fontsize=16)
    page.insert_text((72, 175), "Plan, record, and reflect on your financial goals.", fontsize=11)
    page.insert_text((72, 760), f"Page {index + 1} of 48", fontsize=9)
document.save(OUT)
