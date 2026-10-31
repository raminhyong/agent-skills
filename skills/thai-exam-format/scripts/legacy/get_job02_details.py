import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document("Job02_Formatted.docx")

print("=== JOB02 TABLE DETAILS ===")
for t_idx, table in enumerate(doc.tables):
    print(f"\n--- TABLE {t_idx} ---")
    for r_idx, row in enumerate(table.rows):
        cells = [c.text.strip().replace('\n', ' ') for c in row.cells]
        print(f"Row {r_idx}: {' | '.join(cells)}")

print("\n=== PARAGRAPHS OVERVIEW ===")
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip().replace('\u200b', '')
    if any(k in t for k in ['ผลการเรียนรู้', 'มาตรฐาน', 'คำชี้แจง', 'คำสั่ง', 'เฉลย']):
        print(f"P{i:03d}: {t}")
