import subprocess
import os
import shutil
import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = 'h:/My Drive/งานหัวหน้ากลุ่มสาระฯ รามิล 2569/บันทึกข้อความ'
SCRATCH_DIR = os.path.join(BASE_DIR, 'scratch')
TEMP_DIR = 'C:\\temp_memo'
os.makedirs(TEMP_DIR, exist_ok=True)

def test_file(docx_name, pdf_out_name, prefix):
    src_docx = os.path.join(BASE_DIR, docx_name)
    temp_docx = os.path.join(TEMP_DIR, f"{prefix}.docx")
    temp_pdf = os.path.join(TEMP_DIR, f"{prefix}.pdf")
    final_pdf = os.path.join(SCRATCH_DIR, f"{pdf_out_name}.pdf")
    
    if os.path.exists(temp_pdf):
        try:
            os.remove(temp_pdf)
        except Exception:
            pass
            
    shutil.copy2(src_docx, temp_docx)
    
    ps_content = f'''
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("{temp_docx}")
$doc.SaveAs([ref]"{temp_pdf}", [ref]17)
$doc.Close([ref]$false)
$word.Quit()
'''
    ps_file = os.path.join(TEMP_DIR, f"conv_{prefix}.ps1")
    with open(ps_file, 'w', encoding='utf-8') as f:
        f.write(ps_content)
        
    res = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file], capture_output=True, text=True)
    
    if os.path.exists(temp_pdf):
        shutil.copy2(temp_pdf, final_pdf)
        pdf = pymupdf.open(final_pdf)
        print(f"=== {docx_name} ===")
        print(f"Total PDF pages: {len(pdf)}")
        for i, page in enumerate(pdf):
            img_path = os.path.join(SCRATCH_DIR, f"{prefix}_p{i+1}.png")
            page.get_pixmap(dpi=150).save(img_path)
            print(f"Saved page {i+1} to {img_path}")
    else:
        print(f"Failed to generate PDF for {docx_name}")
        print(res.stderr)

if __name__ == '__main__':
    test_file('บันทึกข้อความไปราชการ3กย69.docx', 'preview_req3sep', 'req3sep')
    test_file('บันทึกข้อความรายงานผลการไปราชการ3กย69.docx', 'preview_rep3sep', 'rep3sep')
