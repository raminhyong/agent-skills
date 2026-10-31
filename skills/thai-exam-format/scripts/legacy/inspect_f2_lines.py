import pymupdf
import re

pdf = pymupdf.open("test_format2_all.pdf")

# Extract text line by line with y-coordinates
for p_idx, page in enumerate(pdf):
    text_page = page.get_text("words")
    # words format: (x0, y0, x1, y1, word, block_no, line_no, word_no)
    lines_dict = {}
    for w in text_page:
        # group words by line_no and block_no
        key = (w[5], w[6])
        if key not in lines_dict:
            lines_dict[key] = []
        lines_dict[key].append(w)
    
    # print each line
    print(f"=== Page {p_idx+1} ===")
    for key in sorted(lines_dict.keys()):
        words_in_line = lines_dict[key]
        line_text = "".join(w[4] for w in words_in_line)
        x0 = min(w[0] for w in words_in_line)
        x1 = max(w[2] for w in words_in_line)
        print(f"  y={words_in_line[0][1]:.1f} x0={x0:.1f} x1={x1:.1f} | {line_text}")
