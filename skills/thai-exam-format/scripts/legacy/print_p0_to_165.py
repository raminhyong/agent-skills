import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document("Job01_Formatted.docx")

for i in range(min(165, len(doc.paragraphs))):
    p = doc.paragraphs[i]
    text = p.text.strip().replace('\u200b', '')
    sb = p.paragraph_format.space_before.pt if p.paragraph_format.space_before else 0
    sa = p.paragraph_format.space_after.pt if p.paragraph_format.space_after else 0
    li = p.paragraph_format.left_indent.inches if p.paragraph_format.left_indent else 0
    fli = p.paragraph_format.first_line_indent.inches if p.paragraph_format.first_line_indent else 0
    
    b_runs = [r.text.replace('\u200b', '') for r in p.runs if r.bold]
    
    info = []
    if sb > 0: info.append(f"sb={sb}")
    if sa > 0: info.append(f"sa={sa}")
    if li > 0: info.append(f"li={li:.2f}\"")
    if fli > 0: info.append(f"fli={fli:.2f}\"")
    if b_runs: info.append(f"BOLD={b_runs}")
    
    info_str = f" [{', '.join(info)}]" if info else ""
    print(f"P{i:03d}{info_str}: {text}")
