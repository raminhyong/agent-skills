import docx
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

target = os.path.join(BASE_DIR, 'Job03_Formatted.docx')
doc = docx.Document(target)

print("=== VERIFYING Job03_Formatted.docx ===\n")

# Check Margins
section = doc.sections[0]
print(f"Margins (in): Top={section.top_margin.inches:.2f}, Bottom={section.bottom_margin.inches:.2f}, Left={section.left_margin.inches:.2f}, Right={section.right_margin.inches:.2f}")

# Check Table 1 Summary
t1 = doc.tables[1]
print(f"\nSummary Table Rows: {len(t1.rows)}")
for r_idx, row in enumerate(t1.rows):
    c0_text = row.cells[0].text.replace('\u200b', '')
    c1_text = row.cells[1].text.replace('\u200b', '')
    c0_align = row.cells[0].paragraphs[0].alignment
    c1_align = row.cells[1].paragraphs[0].alignment
    print(f"  Row {r_idx:02d}: C0='{c0_text}' ({c0_align}) | C1='{c1_text}' ({c1_align})")

# Check Negative words bold
print("\n--- Checking Bold Negative Words in Questions ---")
neg_found_count = 0
for p in doc.paragraphs:
    if p.text and p.text[0].isdigit() and ('. ' in p.text[:5]):
        bold_runs = [r.text for r in p.runs if r.bold]
        if bold_runs:
            print(f"  {p.text[:40]}... -> Bold: {bold_runs}")
            neg_found_count += 1
print(f"Total questions with bolded negative terms: {neg_found_count}")
