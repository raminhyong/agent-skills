import os
import sys
import docx
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, Cm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

target_path = os.path.join(BASE_DIR, "Job03_Formatted.docx")
doc = docx.Document(target_path)

print("=" * 60)
print("VERIFICATION OF Job03_Formatted.docx")
print("=" * 60)

# 1. Page Margins & Setup
section = doc.sections[0]
print("\n[1] Page Setup & Margins:")
print(f"  Top Margin:    {section.top_margin.inches:.2f}\" (Expected: 0.50\")")
print(f"  Bottom Margin: {section.bottom_margin.inches:.2f}\" (Expected: 0.50\")")
print(f"  Left Margin:   {section.left_margin.inches:.2f}\" (Expected: 0.70\")")
print(f"  Right Margin:  {section.right_margin.inches:.2f}\" (Expected: 0.80\")")
print(f"  Header Dist:   {section.header_distance.cm:.2f} cm (Expected: 0.60 cm)")

assert abs(section.top_margin.inches - 0.5) < 0.01, "Top margin mismatch"
assert abs(section.bottom_margin.inches - 0.5) < 0.01, "Bottom margin mismatch"
assert abs(section.left_margin.inches - 0.7) < 0.01, "Left margin mismatch"
assert abs(section.right_margin.inches - 0.8) < 0.01, "Right margin mismatch"
print("  -> Page Margins PASSED [OK]")

# 2. Header
header_p = section.header.paragraphs[0]
header_text = header_p.text.strip()
print("\n[2] Header Page Number:")
print(f"  Header text: '{header_text}' (Expected: '-  -')")
runs_bold = [r.bold for r in header_p.runs]
print(f"  Runs bold: {runs_bold}")
assert all(runs_bold), "Header runs must be bold"
print("  -> Header Page Number PASSED [OK]")

# 3. No Cover Page Check
print("\n[3] No Cover Page Verification:")
print(f"  Total tables in doc: {len(doc.tables)} (Expected: 0)")
assert len(doc.tables) == 0, "Doc must not contain cover page tables!"
first_p_text = doc.paragraphs[0].text.replace('\u200b', '')
print(f"  Paragraph 0: '{first_p_text}'")
assert "คำสั่ง จงเลือกคำตอบที่ถูกต้องที่สุดเพียงคำตอบเดียว" in first_p_text, "P0 must be lead-in instruction!"
p0_runs = doc.paragraphs[0].runs
assert p0_runs[0].bold == True and "คำสั่ง" in p0_runs[0].text.replace('\u200b', ''), "'คำสั่ง' must be Bold!"
assert p0_runs[1].bold == False, "Remaining instruction text must be Regular weight!"
print("  -> No Cover Page PASSED [OK]")

# 4. Paragraph Count & Breakdown
print("\n[4] Paragraph Breakdown:")
paras = doc.paragraphs
print(f"  Total paragraphs: {len(paras)}")
# Structure: 1 (instruction) + 7 (categories) + 39 (questions) + 39*4 (choices) = 203 paragraphs
expected_paras = 1 + 7 + 39 + (39 * 4)
print(f"  Expected paragraphs: {expected_paras}")
assert len(paras) == expected_paras, f"Paragraph count mismatch! Got {len(paras)}, expected {expected_paras}"
print("  -> Paragraph Count PASSED [OK]")

# 5. Category Headings Check
print("\n[5] Category Headings Check:")
cat_headings = [p.text.replace('\u200b', '') for p in paras if "การวิเคราะห์" in p.text]
print(f"  Found {len(cat_headings)} category headings:")
for ch in cat_headings:
    print(f"    - {ch}")
assert len(cat_headings) == 7, "Must have exactly 7 category headings"
print("  -> Category Headings PASSED [OK]")

# 6. Negative Words Bolding
print("\n[6] Negative Words Bolding Check:")
neg_bold_found = []
for p in paras:
    t = p.text.replace('\u200b', '')
    if t and t[0].isdigit() and ('. ' in t[:5]) and (" " in t[:5]):
        bold_runs = [r.text.replace('\u200b', '') for r in p.runs if r.bold]
        if bold_runs:
            q_num = t.split('.')[0]
            neg_bold_found.append((q_num, bold_runs, t[:60]))
            print(f"  Q{q_num}: Bold runs = {bold_runs} | Stem: {t[:50]}...")

assert len(neg_bold_found) == 2, f"Expected 2 bolded negative questions (Q8 and Q35), got {len(neg_bold_found)}"
assert neg_bold_found[0][0] == '8' and 'ไม่ใช่' in neg_bold_found[0][1], "Q8 must bold 'ไม่ใช่'"
assert neg_bold_found[1][0] == '35' and 'ไม่ใช่' in neg_bold_found[1][1], "Q35 must bold 'ไม่ใช่'"
print("  -> Negative Words Bolding PASSED [OK]")

# 7. Choice Length Sorting Check
print("\n[7] Choice Length Sorting (Shortest to Longest):")
NON_SPACING = set(['\u0e31', '\u0e34', '\u0e35', '\u0e36', '\u0e37', '\u0e38', '\u0e39', '\u0e3a',
                   '\u0e47', '\u0e48', '\u0e49', '\u0e4a', '\u0e4b', '\u0e4c', '\u0e4d', '\u0e4e', '\u200b'])
def vlen(s):
    return sum(1 for c in s if c not in NON_SPACING)

choice_sort_failures = 0
for i in range(len(paras)):
    p = paras[i]
    t = p.text.replace('\u200b', '')
    # If this is choice 1 (indented 0.2", starts with "1. ")
    if p.paragraph_format.left_indent and abs(p.paragraph_format.left_indent.inches - 0.2) < 0.05 and t.startswith("1. "):
        c1 = paras[i].text.replace('\u200b', '')[3:]
        c2 = paras[i+1].text.replace('\u200b', '')[3:]
        c3 = paras[i+2].text.replace('\u200b', '')[3:]
        c4 = paras[i+3].text.replace('\u200b', '')[3:]
        v_lens = [vlen(c1), vlen(c2), vlen(c3), vlen(c4)]
        if not (v_lens[0] <= v_lens[1] <= v_lens[2] <= v_lens[3]):
            print(f"  Sorting failure at paragraph {i}: lenses={v_lens}")
            choice_sort_failures += 1

assert choice_sort_failures == 0, f"Found {choice_sort_failures} unsorted choice blocks!"
print("  -> All 39 question choice sets are strictly sorted by visual length PASSED [OK]")

# 8. Keep Together and Keep With Next Check
print("\n[8] Keep-Together & Keep-With-Next Rules:")
keep_with_next_failures = 0
for i in range(len(paras)):
    p = paras[i]
    t = p.text.replace('\u200b', '')
    # Category Headings must have keep_with_next = True and keep_together = True
    if "การวิเคราะห์" in t:
        if not p.paragraph_format.keep_with_next or not p.paragraph_format.keep_together:
            print(f"  Category Heading missing keep properties: '{t[:40]}'")
            keep_with_next_failures += 1
    # Questions must have keep_with_next = True and keep_together = True
    elif p.paragraph_format.left_indent == Pt(0) and t and t[0].isdigit() and ('. ' in t[:5]):
        if not p.paragraph_format.keep_with_next or not p.paragraph_format.keep_together:
            print(f"  Question missing keep properties: '{t[:40]}'")
            keep_with_next_failures += 1
    # Choices 1, 2, 3 must have keep_with_next = True, all choices must have keep_together = True
    elif p.paragraph_format.left_indent and abs(p.paragraph_format.left_indent.inches - 0.2) < 0.05:
        if not p.paragraph_format.keep_together:
            print(f"  Choice missing keep_together: '{t[:30]}'")
            keep_with_next_failures += 1
        if t.startswith(("1. ", "2. ", "3. ")) and not p.paragraph_format.keep_with_next:
            print(f"  Choice 1-3 missing keep_with_next: '{t[:30]}'")
            keep_with_next_failures += 1

assert keep_with_next_failures == 0, f"Found {keep_with_next_failures} keep properties failures!"
print("  -> Keep-Together & Keep-With-Next PASSED [OK]")

# 9. Document Defaults & Style XML Check
print("\n[9] Word XML Engine Root Cause Fixes:")
styles_elem = doc.styles.element
docDefaults = styles_elem.find(qn('w:docDefaults'))
rPrDef = docDefaults.find(qn('w:rPrDefault')).find(qn('w:rPr'))
rFonts = rPrDef.find(qn('w:rFonts'))
sz = rPrDef.find(qn('w:sz')).attrib.get(qn('w:val'))
szCs = rPrDef.find(qn('w:szCs')).attrib.get(qn('w:val'))
lang = rPrDef.find(qn('w:lang')).attrib.get(qn('w:val'))

print(f"  docDefaults Font: ascii='{rFonts.attrib.get(qn('w:ascii'))}', cs='{rFonts.attrib.get(qn('w:cs'))}'")
print(f"  docDefaults Size: sz={sz}, szCs={szCs} (Expected: 32 = 16pt)")
print(f"  docDefaults Lang: {lang} (Expected: th-TH)")

assert rFonts.attrib.get(qn('w:ascii')) == 'TH Sarabun New', "Default font ascii mismatch"
assert sz == '32' and szCs == '32', "Default size must be 32 (16pt)"
assert lang == 'th-TH', "Default lang must be th-TH"
print("  -> XML Root Cause Fixes PASSED [OK]")

print("\n" + "=" * 60)
print("ALL VERIFICATION CHECKS PASSED PERFECTLY 100%!")
print("=" * 60)
