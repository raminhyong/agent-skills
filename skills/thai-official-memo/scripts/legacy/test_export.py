import subprocess
import os
import shutil
import pymupdf

os.makedirs('C:\\temp_memo', exist_ok=True)
src_docx = os.path.abspath('บันทึกข้อความไปราชการ17สค69.docx')
temp_docx = 'C:\\temp_memo\\memo.docx'
temp_pdf = 'C:\\temp_memo\\preview17.pdf'
final_pdf = os.path.abspath('scratch/preview17.pdf')

if os.path.exists(temp_pdf):
    try:
        os.remove(temp_pdf)
    except Exception:
        pass

shutil.copy2(src_docx, temp_docx)

ps_script = f'''
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("{temp_docx}")
$doc.SaveAs([ref]"{temp_pdf}", [ref]17)
$doc.Close([ref]$false)
$word.Quit()
'''

with open('C:\\temp_memo\\conv.ps1', 'w', encoding='utf-8') as f:
    f.write(ps_script)

res = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'C:\\temp_memo\\conv.ps1'], capture_output=True, text=True)
print('STDOUT:', res.stdout)
print('STDERR:', res.stderr)

if os.path.exists(temp_pdf):
    shutil.copy2(temp_pdf, final_pdf)
    pdf = pymupdf.open(final_pdf)
    print(f'Total PDF pages: {len(pdf)}')
    for i, page in enumerate(pdf):
        page.get_pixmap(dpi=150).save(f'scratch/preview17_p{i+1}.png')
    print('Rendered preview images successfully.')
else:
    print('PDF not generated.')
