import os
import win32com.client

doc_path = os.path.abspath("d:/MEGA/บันทึกข้อความ/บันทึกข้อความ/บันทึกข้อความส่งบันทึกหลังแผนการจัดการเรียนรู้ 1-2569.docx")
pdf_path = os.path.abspath("d:/MEGA/บันทึกข้อความ/บันทึกข้อความ/scratch/preview_post_lesson_memo.pdf")

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

try:
    doc = word.Documents.Open(doc_path)
    # wdStatisticPages = 2
    pages = doc.ComputeStatistics(2)
    print(f"Word Page Count: {pages}")
    
    # Save as PDF (wdFormatPDF = 17)
    doc.SaveAs(pdf_path, FileFormat=17)
    doc.Close(False)
    print(f"Exported to: {pdf_path}")
finally:
    word.Quit()
