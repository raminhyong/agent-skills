import docx
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def analyze_job02():
    doc = docx.Document("Job02_Formatted.docx")
    print(f"Total paragraphs in Job02_Formatted.docx: {len(doc.paragraphs)}")
    print(f"Total tables: {len(doc.tables)}")
    
    # Let's inspect the first 25 paragraphs (Header, Instructions, Indicators, Signatures)
    print("\n--- COVER & META INFO ---")
    for i in range(min(25, len(doc.paragraphs))):
        t = doc.paragraphs[i].text.strip().replace('\u200b', '')
        if t:
            print(f"P{i:02d}: {t}")
            
    # Extract questions and their choices
    questions = []
    current_q = None
    
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip().replace('\u200b', '')
        if not t: continue
        
        m = re.match(r'^(\d+)\.\s+(.*)', t)
        is_choice = bool(p.paragraph_format.left_indent and p.paragraph_format.left_indent.inches == 0.2) or '\t2.' in t or '\tข.' in t
        
        if m and not is_choice and not t.startswith("1. ข้อสอบ") and not t.startswith("2. ไม่") and not t.startswith("3. ไม่"):
            q_num = int(m.group(1))
            if current_q:
                questions.append(current_q)
            current_q = {'num': q_num, 'stem': m.group(2), 'lines': []}
        elif current_q:
            if 'เฉลย' in t:
                questions.append(current_q)
                current_q = None
                break
            current_q['lines'].append(t)
            
    if current_q:
        questions.append(current_q)
        
    print(f"\n--- FOUND {len(questions)} QUESTIONS ---")
    for q in questions:
        print(f"\nข้อ {q['num']}: {q['stem']}")
        for l in q['lines']:
            print(f"    {l}")

if __name__ == "__main__":
    analyze_job02()
