import os
import sys
import time
import win32com.client
import pymupdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docx_path = os.path.join(BASE_DIR, "Job02_Formatted.docx")
pdf_path = os.path.join(BASE_DIR, "Job02_Formatted.pdf")
preview_dir = os.path.join(BASE_DIR, "previews_job02")

os.makedirs(preview_dir, exist_ok=True)

# Kill any existing Word instance
os.system('taskkill /f /im WINWORD.EXE 2>nul')
time.sleep(0.8)

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0

try:
    doc = word.Documents.Open(docx_path)
    doc.SaveAs2(pdf_path, FileFormat=17) # 17 = wdFormatPDF
    doc.Close(False)
    print(f"Exported PDF successfully: {pdf_path}")
finally:
    word.Quit()

# Render pages to PNG
pdf_doc = pymupdf.open(pdf_path)
print(f"Total Pages in PDF: {len(pdf_doc)}")

for page_num in range(len(pdf_doc)):
    page = pdf_doc[page_num]
    pix = page.get_pixmap(dpi=150)
    img_out = os.path.join(preview_dir, f"page_{page_num+1}.png")
    pix.save(img_out)
    print(f"Saved: {img_out}")

print("Done rendering all pages!")
