import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('Job03.json', encoding='utf-8-sig'))

NON_SPACING = set(['\u0e31', '\u0e34', '\u0e35', '\u0e36', '\u0e37', '\u0e38', '\u0e39', '\u0e3a',
                   '\u0e47', '\u0e48', '\u0e49', '\u0e4a', '\u0e4b', '\u0e4c', '\u0e4d', '\u0e4e', '\u200b'])

def vlen(s):
    return sum(1 for c in s if c not in NON_SPACING)

layout_counts = {'1 line': 0, '2 lines': 0, '4 lines': 0}

for d in data:
    opts = list(d['options'].values())
    sorted_opts = sorted(opts, key=lambda o: vlen(o))
    lens = [vlen(o) for o in sorted_opts]
    max_l = max(lens)
    layout = '1 line' if max_l <= 10 else ('2 lines' if max_l <= 25 else '4 lines')
    layout_counts[layout] += 1
    print(f"Q{d['no']:02d}: max_vlen={max_l:02d} -> layout={layout:7s} | sorted lens={lens}")

print('\nLayout summary:', layout_counts)
