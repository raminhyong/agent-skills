import docx

doc = docx.Document('d:/MEGA/บันทึกข้อความ/บันทึกข้อความ/บันทึกข้อความส่งแผนการสอน.docx')
with open('d:/MEGA/บันทึกข้อความ/บันทึกข้อความ/scratch/inspect_full_plan_memo.txt', 'w', encoding='utf-8') as f:
    f.write(f"Num paragraphs: {len(doc.paragraphs)}\n")
    for i, p in enumerate(doc.paragraphs):
        f.write(f"P{i}: text={repr(p.text)}\n")
        # Check xml for page break
        if 'w:br' in p._p.xml:
            f.write("   --> Contains PageBreak or LineBreak\n")
    f.write(f"\nNum tables: {len(doc.tables)}\n")
    for ti, t in enumerate(doc.tables):
        f.write(f"Table {ti}: rows={len(t.rows)}, cols={len(t.columns)}\n")
        for ri, r in enumerate(t.rows):
            f.write(f"  Row {ri}: {[c.text.strip().replace('\n', ' ') for c in r.cells]}\n")

print("Done")
