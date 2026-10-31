import os
import sys
import time
import docx
from docx.shared import Inches, Pt
import win32com.client
import pymupdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "scripts"))
from format_job02 import build_job02_docx

# Let's inspect modifying section header_distance and margins
doc = docx.Document(os.path.join(BASE_DIR, "Job02_Formatted.docx"))
section = doc.sections[0]
section.header_distance = Inches(0.3)
section.footer_distance = Inches(0.3)
section.top_margin = Inches(0.45)
section.bottom_margin = Inches(0.45)
section.left_margin = Inches(0.7)
section.right_margin = Inches(0.75)

test_docx = os.path.join(BASE_DIR, "test_job02.docx")
test_pdf = os.path.join(BASE_DIR, "test_job02.pdf")

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

pdf_doc = pymupdf.open(test_pdf)
print(f"Test PDF Total Pages: {len(pdf_doc)}")

import re
for i in range(1, len(pdf_doc)):
    page = pdf_doc[i]
    text = page.get_text()
    q_matches = re.findall(r'(?:^|\n)(\d+)\.\s*', text)
    seen = []
    for q in q_matches:
        if q not in seen:
            seen.append(q)
    print(f"Page {i+1}: Questions: {seen} (count: {len(seen)})")
