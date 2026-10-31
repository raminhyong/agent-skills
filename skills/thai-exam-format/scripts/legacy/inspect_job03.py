import docx
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document(os.path.join(BASE_DIR, 'Job03.docx'))
print(f"Total paragraphs in Job03.docx: {len(doc.paragraphs)}")

for i in range(min(50, len(doc.paragraphs))):
    print(f"P{i:03d}: {doc.paragraphs[i].text}")
