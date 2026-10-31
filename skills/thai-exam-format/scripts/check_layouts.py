import docx
import re
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding='utf-8')

NON_SPACING_CHARS = set([
    '\u0e31', '\u0e34', '\u0e35', '\u0e36', '\u0e37', '\u0e38', '\u0e39', '\u0e3a',
    '\u0e47', '\u0e48', '\u0e49', '\u0e4a', '\u0e4b', '\u0e4c', '\u0e4d', '\u0e4e',
    '\u200b'
])

def visual_length(text):
    return sum(1 for c in text if c not in NON_SPACING_CHARS)

from check_all_q import questions

for q in questions:
    q_num = q['num']
    choices = q['choices']
    sorted_choices = sorted(choices, key=lambda c: visual_length(c))
    v_lens = [visual_length(c) for c in sorted_choices]
    max_v = max(v_lens) if v_lens else 0
    
    if max_v <= 10 and len(sorted_choices) == 4:
        layout = "Format 3 (1-line: 4 cols -> 0.2, 1.8, 3.4, 5.0 in)"
    elif max_v <= 25 and len(sorted_choices) == 4:
        layout = "Format 2 (2-line: 2 cols -> 0.2, 3.4 in)"
    else:
        layout = "Format 1 (4-line: 1 col -> 0.2 in)"
        
    print(f"Q{q_num:02d}: max_v={max_v:2d} -> {layout}")
