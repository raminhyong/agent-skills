import docx
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def inspect_full_job02():
    doc = docx.Document("Job02_Formatted.docx")
    
    # Meta / Cover info
    print("=== HEADER / META ===")
    for t in doc.tables:
        for r in t.rows:
            row_txt = [c.text.strip().replace('\n', ' ') for c in r.cells]
            print(" | ".join(row_txt))
            
    print("\n=== QUESTIONS ===")
    current_std = ""
    for p in doc.paragraphs:
        t = p.text.strip().replace('\u200b', '')
        if not t: continue
        if 'ผลการเรียนรู้' in t or 'มาตรฐาน' in t:
            current_std = t
            print(f"\n>>> {t}")
        elif re.match(r'^\d+\.\s+', t):
            print(f"\n{t}")
        elif p.paragraph_format.left_indent and p.paragraph_format.left_indent.inches == 0.2:
            print(f"    {t}")
        elif '\t' in t and (t.startswith('1.') or t.startswith('3.')):
            print(f"    {t}")
        elif 'เฉลย' in t or '①' in t or '②' in t:
            print(f"\n[KEY] {t}")

if __name__ == "__main__":
    inspect_full_job02()
