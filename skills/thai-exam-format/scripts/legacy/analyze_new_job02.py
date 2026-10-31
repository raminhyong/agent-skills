import json
import os
import re

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

print("=== QUESTION & CHOICE LENGTH ANALYSIS ===")
for q in questions:
    q_num = q['num']
    q_text = q['text']
    choices = q['sorted_choices']
    lens = [visual_length(c) for c in choices]
    max_len = max(lens)
    
    # Check layout feasibility:
    # 4 col (1 line): max_len <= 12
    # 2 col (2 lines): max_len <= 26
    # 1 col (4 lines): otherwise
    if max_len <= 12:
        layout = "1-line (4 cols)"
    elif max_len <= 26:
        layout = "2-lines (2 cols)"
    else:
        layout = "4-lines (1 col)"
        
    print(f"Q{q_num:02d}: max_len={max_len:2d}, layout={layout:16s} | lengths={lens}")
    for idx, c in enumerate(choices, 1):
        print(f"    {idx}. ({visual_length(c):2d} chars) {c}")
