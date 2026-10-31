import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')
for fn in ['Job01_Formatted.docx', 'Job02_Formatted.docx']:
    try:
        doc = docx.Document(fn)
        print(f'=== {fn} ===')
        for i, p in enumerate(doc.paragraphs):
            t = p.text
            if any(c in t for c in ['"', '“', '”', 'พิจารณา']):
                print(f'  P{i:03d} (indent={p.paragraph_format.left_indent}): {t[:80]}')
    except Exception as e:
        print(f'Error reading {fn}: {e}')
