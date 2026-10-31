import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "scripts", "job02_new_parsed.json"), "r", encoding="utf-8") as f:
    questions = json.load(f)

NON_SPACING_CHARS = set([
    '\u0e31', '\u0e34', '\u0e35', '\u0e36', '\u0e37', '\u0e38', '\u0e39', '\u0e3a',
    '\u0e47', '\u0e48', '\u0e49', '\u0e4a', '\u0e4b', '\u0e4c', '\u0e4d', '\u0e4e',
    '\u200b'
])

def visual_length(text):
    return sum(1 for c in text if c not in NON_SPACING_CHARS)

out_lines = []
for q in questions:
    q_num = q['num']
    sorted_choices = q['sorted_choices']
    v_lens = [visual_length(c) for c in sorted_choices]
    max_len = max(v_lens)
    out_lines.append(f"Q{q_num:02d}: max={max_len} | {q['text']}")
    for idx, c in enumerate(sorted_choices, 1):
        out_lines.append(f"    {idx}. ({visual_length(c):2d} chars) {c}")

with open(os.path.join(BASE_DIR, "scripts", "choices_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print("Saved choices_summary.txt successfully.")
