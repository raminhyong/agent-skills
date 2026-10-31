import docx
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

target = os.path.join(BASE_DIR, 'Job02_Formatted_v2.docx')
if not os.path.exists(target):
    target = os.path.join(BASE_DIR, 'Job02_Formatted.docx')
doc = docx.Document(target)

print('=== 1. Checking Page 1 Headings Boldness ===')
p_school = doc.paragraphs[1]
print('School Name:', p_school.text, 'Bold:', [r.bold for r in p_school.runs])
p_inst = doc.paragraphs[2]
print('Instructions:', p_inst.text, 'Bold:', [r.bold for r in p_inst.runs])

print('\n=== 2. Checking Learning Outcomes Headings ===')
for i, p in enumerate(doc.paragraphs):
    if 'ผล' in p.text and 'การเรียนรู้ที่' in p.text:
        has_dash = '-' in p.text or '—' in p.text or '–' in p.text
        print(f'P{i}: {p.text} | Has Dash? {has_dash}')

print('\n=== 3. Checking Signature Block Alignment ===')
sig_tbl = doc.tables[2]
for r_idx, r in enumerate(sig_tbl.rows):
    print(f'-- Sig Row {r_idx} --')
    for c_idx, c in enumerate(r.cells):
        for p in c.paragraphs:
            tabs = [(ts.position.inches, str(ts.alignment)) for ts in p.paragraph_format.tab_stops]
            indent = p.paragraph_format.left_indent.inches if p.paragraph_format.left_indent else 0
            print(f'  Cell ({r_idx},{c_idx}) indent={indent} in: text="{p.text}", tabs={tabs}')

print('\n=== 4. Checking Negative Words in Questions ===')
for i, p in enumerate(doc.paragraphs):
    if p.text and p.text[0].isdigit() and any(k in p.text for k in ['ไม่', 'มิได้', 'ยกเว้น']):
        bold_runs = [r.text for r in p.runs if r.bold]
        print(f'Question: {p.text[:50]}... -> Bold runs: {bold_runs}')
