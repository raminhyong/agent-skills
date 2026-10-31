import os
import pymupdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for fname in ["Master.pdf"]:
    p = os.path.join(BASE_DIR, fname)
    if os.path.exists(p):
        doc = pymupdf.open(p)
        print(f"File {fname}: total pages = {len(doc)}")
        for i in range(len(doc)):
            print(f"  Page {i+1}: text length = {len(doc[i].get_text())}")
