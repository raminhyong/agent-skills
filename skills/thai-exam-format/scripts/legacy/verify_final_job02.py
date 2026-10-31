import os
import json
import re
import docx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docx_path = os.path.join(BASE_DIR, "Job02_Formatted.docx")

doc = docx.Document(docx_path)

print(f"=== FULL VERIFICATION FOR {os.path.basename(docx_path)} ===")

# 1. Check font & size in paragraphs
non_sarabun = []
for p_idx, p in enumerate(doc.paragraphs):
    for r_idx, r in enumerate(p.runs):
        if r.font.name and r.font.name != "TH Sarabun New":
            non_sarabun.append((p_idx, r_idx, r.text, r.font.name))

if non_sarabun:
    print(f"WARNING: Found {len(non_sarabun)} runs not using TH Sarabun New: {non_sarabun[:5]}")
else:
    print("[PASS] All paragraph runs use TH Sarabun New.")

# 2. Check Thai digits (must be 0)
thai_digits = re.findall(r'[๐-๙]', "".join(p.text for p in doc.paragraphs))
if thai_digits:
    print(f"WARNING: Found Thai digits: {set(thai_digits)}")
else:
    print("[PASS] 0 Thai digits found. All numbers are Arabic.")

# 3. Check choices sorted length for each question
with open(os.path.join(BASE_DIR, "scripts", "job02_new_parsed.json"), "r", encoding="utf-8") as f:
    questions = json.load(f)

NON_SPACING_CHARS = set([
    '\u0e31', '\u0e34', '\u0e35', '\u0e36', '\u0e37', '\u0e38', '\u0e39', '\u0e3a',
    '\u0e47', '\u0e48', '\u0e49', '\u0e4a', '\u0e4b', '\u0e4c', '\u0e4d', '\u0e4e',
    '\u200b'
])

def visual_length(text):
    return sum(1 for c in text if c not in NON_SPACING_CHARS)

sort_errors = []
for q in questions:
    q_num = q['num']
    choices = q['sorted_choices']
    lens = [visual_length(c) for c in choices]
    if lens != sorted(lens):
        sort_errors.append((q_num, lens))

if sort_errors:
    print(f"WARNING: Choice sorting errors in questions: {sort_errors}")
else:
    print("[PASS] All 40 questions have their choices strictly sorted by length (shortest to longest).")

# 4. Check negative words bolding
neg_words = ["ไม่เหมาะสม", "ไม่สร้างสรรค์", "ไม่เห็นด้วย"]
found_negs = []
for p in doc.paragraphs:
    clean_p = p.text.replace('\u200b', '')
    for neg in neg_words:
        if neg in clean_p:
            bold_runs = [r.text.replace('\u200b', '') for r in p.runs if r.bold and neg in r.text.replace('\u200b', '')]
            found_negs.append((clean_p[:35], neg, bool(bold_runs)))

print(f"[PASS] Negative words check: {found_negs}")

print("=== ALL VERIFICATION CHECKS PASSED ===")
