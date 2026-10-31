import docx
import sys
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document(os.path.join(BASE_DIR, 'Job03.docx'))

print("=== Paragraph 208 Inspection ===")
p208 = doc.paragraphs[208].text
print("Raw p208:", repr(p208))

pattern = r'(ว\s*\d+\.\d+\s*ม\.\d+/\d+)\s*(.*?)(?=(?:ว\s*\d+\.\d+\s*ม\.\d+/\d+)|$)'
matches = re.findall(pattern, p208)
print(f"Found {len(matches)} indicators in p208:")
for ind, desc in matches:
    print(f"  Indicator: [{ind.strip()}] -> Description: [{desc.strip()}]")
