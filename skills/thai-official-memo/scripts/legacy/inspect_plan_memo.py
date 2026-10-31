import os
import docx

def inspect_doc(path, out_f):
    out_f.write(f"\n========================================\nFILE: {path}\n========================================\n")
    if not os.path.exists(path):
        out_f.write("FILE DOES NOT EXIST!\n")
        return
    doc = docx.Document(path)
    out_f.write("--- PARAGRAPHS ---\n")
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t:
            out_f.write(f"P{i}: {t}\n")
            for r in p.runs:
                if r.text.strip():
                    out_f.write(f"   [run: bold={r.bold}, size={r.font.size}]: {r.text}\n")
    out_f.write("\n--- TABLES ---\n")
    for ti, t in enumerate(doc.tables):
        out_f.write(f"\nTable {ti} (rows={len(t.rows)}, cols={len(t.columns)}):\n")
        for ri, r in enumerate(t.rows):
            row_texts = [cell.text.strip().replace('\n', ' // ') for cell in r.cells]
            out_f.write(f"  Row {ri}: {row_texts}\n")

with open("d:/MEGA/บันทึกข้อความ/บันทึกข้อความ/scratch/inspect_plan_memo.txt", "w", encoding="utf-8") as out:
    # 1. Inspect บันทึกข้อความส่งแผนการสอน.docx
    inspect_doc("d:/MEGA/บันทึกข้อความ/บันทึกข้อความ/บันทึกข้อความส่งแผนการสอน.docx", out)
    
    # 2. Inspect files in H: Drive
    h_dir = r"H:\My Drive\งานหัวหน้ากลุ่มสาระฯ รามิล 2569\บันทึกข้อความ\แบบขออนุมัติใช้แผนการสอน"
    out.write(f"\n\n========================================\nH DRIVE FOLDER: {h_dir}\n========================================\n")
    if os.path.exists(h_dir):
        files = sorted(os.listdir(h_dir))
        out.write(f"Found {len(files)} files:\n")
        for f in files:
            out.write(f" - {f}\n")
        for f in files:
            fpath = os.path.join(h_dir, f)
            inspect_doc(fpath, out)
    else:
        out.write("H DIR DOES NOT EXIST!\n")

print("Inspection completed.")
