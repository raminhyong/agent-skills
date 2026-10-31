import pymupdf
import re

doc = pymupdf.open("Job02_Formatted.pdf")
print("Page count:", len(doc))

for i in range(1, len(doc)):
    page = doc[i]
    text = page.get_text()
    q_matches = re.findall(r'(?:^|\n)(\d+)\.\s*', text)
    # unique q_nums in order
    seen = []
    for q in q_matches:
        if q not in seen:
            seen.append(q)
    print(f"Page {i+1}: Questions: {seen} (count: {len(seen)})")
