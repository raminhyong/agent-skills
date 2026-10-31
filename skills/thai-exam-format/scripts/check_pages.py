import os
import pymupdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(BASE_DIR, "Job02_Formatted.pdf")

doc = pymupdf.open(pdf_path)
print(f"Total pages: {len(doc)}")

for idx, page in enumerate(doc, 1):
    text = page.get_text()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    print(f"--- PAGE {idx} (total lines: {len(lines)}) ---")
    print("\n".join(lines[:10]))
    if len(lines) > 10:
        print("...")
        print("\n".join(lines[-5:]))
    print()
