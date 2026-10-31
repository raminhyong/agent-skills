import json
import re

NEGATIVE_WORDS = [
    "ไม่ถูกต้องเหมาะสม", "ไม่ถูกต้อง", "ไม่เหมาะสม", "ไม่ใช่", "ไม่มีประสิทธิภาพ", "ไม่มี",
    "ไม่ปรากฏ", "ไม่จำเป็น", "ไม่ได้", "ไม่ควร", "มิได้", "ยกเว้น", "ไม่"
]

def format_stem_runs(q_num, q_text):
    """
    Format question runs, ensuring negative words are bolded ONLY in question stems,
    NEVER inside quotes/literary excerpts.
    """
    # Regex for negative words
    neg_pattern = "(" + "|".join([re.escape(w) for w in NEGATIVE_WORDS]) + ")"
    
    # Check if text contains quotes: e.g. "..." or “...”
    # If quote exists, separate quote from non-quote
    parts_by_quote = re.split(r'("[^"]*?"|“[^”]*?”)', q_text)
    
    runs = []
    for chunk in parts_by_quote:
        if not chunk:
            continue
        if (chunk.startswith('"') and chunk.endswith('"')) or (chunk.startswith('“') and chunk.endswith('”')):
            # Inside quote: DO NOT bold any negative words!
            runs.append((chunk, False))
        else:
            # Outside quote: can bold negative words
            sub_parts = re.split(neg_pattern, chunk)
            for sp in sub_parts:
                if not sp:
                    continue
                if sp in NEGATIVE_WORDS:
                    runs.append((sp, True))
                else:
                    runs.append((sp, False))
    return runs

data = json.load(open('Job03.json', encoding='utf-8-sig'))
for d in data:
    runs = format_stem_runs(d['no'], d['question'])
    bolded = [t for t, b in runs if b]
    if bolded:
        print(f"Q{d['no']:02d} bolded: {bolded}")
        print("  Runs:", [(t[:20], b) for t, b in runs if b or len(t) < 30])
