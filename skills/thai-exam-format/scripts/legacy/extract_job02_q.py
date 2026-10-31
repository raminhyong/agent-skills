import docx
import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document("Job02_Formatted.docx")

questions = []
current_lo = ""
current_q = None

for p in doc.paragraphs:
    t = p.text.strip().replace('\u200b', '')
    if not t: continue
    
    if 'ผลการเรียนรู้ที่' in t:
        current_lo = t
        continue
        
    m = re.match(r'^(\d+)\.\s+(.*)', t)
    is_choice = bool(p.paragraph_format.left_indent and p.paragraph_format.left_indent.inches == 0.2) or '\t2.' in t
    
    if m and not is_choice and not t.startswith("1. ข้อสอบ") and not t.startswith("2. ไม่") and not t.startswith("3. ไม่"):
        if current_q:
            questions.append(current_q)
        current_q = {
            'num': int(m.group(1)),
            'lo': current_lo,
            'stem': m.group(2),
            'choices': []
        }
    elif current_q:
        if 'เฉลย' in t or '①' in t:
            questions.append(current_q)
            current_q = None
            break
        # Check if choice line
        c_matches = re.findall(r'[1-4]\.\s*([^\t]+)', t)
        if c_matches:
            for cm in c_matches:
                current_q['choices'].append(cm.strip())
        else:
            if not t.startswith('ผลการเรียนรู้'):
                current_q['choices'].append(t.strip())

if current_q:
    questions.append(current_q)

print(f"Extracted {len(questions)} questions.")

with open("scripts/job02_extracted_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("Saved to scripts/job02_extracted_questions.json")
