import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scripts/job02_extracted_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

for q in questions[:20]:
    print(f"\n==========================================")
    print(f"ข้อ {q['num']}: {q['stem']}")
    print(f"LO: {q['lo']}")
    for idx, c in enumerate(q['choices'], 1):
        print(f"  {idx}. {c}")
