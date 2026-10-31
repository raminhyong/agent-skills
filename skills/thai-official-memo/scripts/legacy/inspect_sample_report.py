import subprocess
import os
import shutil
import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

final_pdf = os.path.abspath('scratch/sample_report.pdf')

if os.path.exists(final_pdf):
    pdf = pymupdf.open(final_pdf)
    print(f'Total PDF pages: {len(pdf)}')
    for i, page in enumerate(pdf):
        page.get_pixmap(dpi=150).save(f'scratch/sample_report_p{i+1}.png')
        print(f'--- PAGE {i+1} ---')
        print(page.get_text())
    print('Rendered sample report images.')
