import os
import sys
import time
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
import pythainlp
import re
import json
import win32com.client
import pymupdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NON_SPACING_CHARS = set([
    '\u0e31', '\u0e34', '\u0e35', '\u0e36', '\u0e37', '\u0e38', '\u0e39', '\u0e3a',
    '\u0e47', '\u0e48', '\u0e49', '\u0e4a', '\u0e4b', '\u0e4c', '\u0e4d', '\u0e4e',
    '\u200b'
])

def visual_length(text):
    return sum(1 for c in text if c not in NON_SPACING_CHARS)

def thai_tokenize(text):
    if not text:
        return ""
    words = pythainlp.word_tokenize(text, engine="newmm")
    res = "\u200b".join(words)
    for c in NON_SPACING_CHARS:
        res = res.replace(f"\u200b{c}", c)
    res = re.sub(r'\u200b+', '\u200b', res)
    return res

def set_run_font(run, font_name="TH Sarabun New", size_pt=16, bold=False, italic=False):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}" w:eastAsia="{font_name}"/>')
        rPr.append(rFonts)
    else:
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:cs'), font_name)
        rFonts.set(qn('w:eastAsia'), font_name)

with open(os.path.join(BASE_DIR, "scripts", "job02_new_parsed.json"), "r", encoding="utf-8") as f:
    questions = json.load(f)

# Let's test all 40 questions formatted in Format 2 in a test docx
doc = docx.Document()
section = doc.sections[0]
section.top_margin = Inches(0.5)
section.bottom_margin = Inches(0.5)
section.left_margin = Inches(0.7)
section.right_margin = Inches(0.8)
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)

for q in questions:
    q_num = q['num']
    choices = q['sorted_choices']
    
    p_q = doc.add_paragraph()
    p_q.paragraph_format.space_before = Pt(0)
    p_q.paragraph_format.space_after = Pt(0)
    p_q.paragraph_format.left_indent = Pt(0)
    r = p_q.add_run(f"{q_num}. " + thai_tokenize(q['text']))
    set_run_font(r)
    
    # Line 1: Choice 1 and Choice 2
    p_c1 = doc.add_paragraph()
    p_c1.paragraph_format.space_before = Pt(0)
    p_c1.paragraph_format.space_after = Pt(0)
    p_c1.paragraph_format.left_indent = Inches(0.2)
    p_c1.paragraph_format.tab_stops.add_tab_stop(Inches(3.4), WD_TAB_ALIGNMENT.LEFT)
    r1 = p_c1.add_run("1. " + thai_tokenize(choices[0]))
    set_run_font(r1)
    r2 = p_c1.add_run("\t2. " + thai_tokenize(choices[1]))
    set_run_font(r2)
    
    # Line 2: Choice 3 and Choice 4
    p_c2 = doc.add_paragraph()
    p_c2.paragraph_format.space_before = Pt(0)
    p_c2.paragraph_format.space_after = Pt(0)
    p_c2.paragraph_format.left_indent = Inches(0.2)
    p_c2.paragraph_format.tab_stops.add_tab_stop(Inches(3.4), WD_TAB_ALIGNMENT.LEFT)
    r3 = p_c2.add_run("3. " + thai_tokenize(choices[2]))
    set_run_font(r3)
    r4 = p_c2.add_run("\t4. " + thai_tokenize(choices[3]))
    set_run_font(r4)

test_docx = os.path.join(BASE_DIR, "test_format2_all.docx")
test_pdf = os.path.join(BASE_DIR, "test_format2_all.pdf")

doc.save(test_docx)

os.system('taskkill /f /im WINWORD.EXE 2>nul')
time.sleep(0.5)

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0

try:
    d = word.Documents.Open(test_docx)
    d.SaveAs2(test_pdf, FileFormat=17)
    d.Close(False)
finally:
    word.Quit()

pdf = pymupdf.open(test_pdf)
print(f"Total pages in all-Format 2 test: {len(pdf)}")

# Check wrapping for each question
# In PyMuPDF, if a paragraph wrapped, p_c1 or p_c2 will occupy more vertical span or multiple text lines
for page_idx in range(len(pdf)):
    page = pdf[page_idx]
    blocks = page.get_text("blocks")
    print(f"--- Page {page_idx+1} ({len(blocks)} blocks) ---")

print("Done evaluating Format 2.")
