import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import win32com.client
import fitz # PyMuPDF

def convert_docx_to_pdf_and_png(docx_path, pdf_path, out_dir):
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    try:
        doc = word.Documents.Open(os.path.abspath(docx_path))
        doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17) # 17 = wdFormatPDF
        doc.Close()
    finally:
        word.Quit()
    
    print(f"PDF generated: {pdf_path}")
    
    # Open PDF with fitz
    pdf_doc = fitz.open(pdf_path)
    print(f"Total pages in PDF: {len(pdf_doc)}")
    
    for i, page in enumerate(pdf_doc):
        pix = page.get_pixmap(dpi=150)
        img_path = os.path.join(out_dir, f"exam_memo_page_{i+1}.png")
        pix.save(img_path)
        print(f"Page {i+1} saved to {img_path}")

if __name__ == '__main__':
    docx_path = r'h:\My Drive\งานหัวหน้ากลุ่มสาระฯ รามิล 2569\บันทึกข้อความ\บันทึกข้อความส่งข้อสอบปลายภาคเรียน 1-2569.docx'
    pdf_path = r'h:\My Drive\งานหัวหน้ากลุ่มสาระฯ รามิล 2569\บันทึกข้อความ\scratch\preview_exam_memo.pdf'
    out_dir = r'h:\My Drive\งานหัวหน้ากลุ่มสาระฯ รามิล 2569\บันทึกข้อความ\scratch'
    convert_docx_to_pdf_and_png(docx_path, pdf_path, out_dir)
