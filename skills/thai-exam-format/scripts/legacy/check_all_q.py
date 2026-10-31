import docx
import re
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document(os.path.join(BASE_DIR, 'Job03.docx'))

NEGATIVE_WORDS = [
    "ไม่ถูกต้องเหมาะสม", "ไม่ถูกต้อง", "ไม่เหมาะสม", "ไม่ใช่", "ไม่มีประสิทธิภาพ", "ไม่มี",
    "ไม่ปรากฏ", "ไม่จำเป็น", "ไม่ได้", "ไม่ควร", "มิได้", "ยกเว้น", "ไม่"
]

questions = []
current_q = None

for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    if not text or i == 208:
        continue
    m = re.match(r'^(\d+)\.\s*(?:\[(.*?)\])?\s*(.*)', text)
    if m:
        if current_q:
            questions.append(current_q)
        current_q = {
            'num': int(m.group(1)),
            'indicator': re.sub(r'\s+', ' ', m.group(2).strip()) if m.group(2) else '',
            'text': m.group(3).strip(),
            'choices': []
        }
    elif current_q and re.match(r'^[ก-ฮa-zA-Z1-4][\.\)]\s*', text):
        c_text = re.sub(r'^[ก-ฮa-zA-Z1-4][\.\)]\s*', '', text).strip()
        current_q['choices'].append(c_text)

if current_q:
    questions.append(current_q)

print(f"Total questions: {len(questions)}")

for q in questions:
    q_text = q['text']
    found = []
    for w in NEGATIVE_WORDS:
        if w in q_text:
            found.append(w)
    if found:
        print(f"Q{q['num']:02d} has negative: {found} -> Text: {q_text}")

# Check any formula or special notation
print("\n--- Formulas & Special Notations ---")
for q in questions:
    if any(ch in q['text'] for ch in ['=', '²', '₁', '₂', 'F', 'G', 'm', 'r', '°']):
        print(f"Q{q['num']:02d}: {q['text']}")
    for c in q['choices']:
        if any(ch in c for ch in ['=', '²', '₁', '₂', 'F', 'G', 'm', 'r', '°']):
            print(f"  Choice in Q{q['num']:02d}: {c}")
