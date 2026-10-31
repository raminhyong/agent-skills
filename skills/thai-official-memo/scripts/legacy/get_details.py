import os
import re
import docx

h_dir = r"H:\My Drive\งานหัวหน้ากลุ่มสาระฯ รามิล 2569\บันทึกข้อความ\แบบขออนุมัติใช้แผนการสอน"
files = sorted(os.listdir(h_dir))

with open("d:/MEGA/บันทึกข้อความ/บันทึกข้อความ/scratch/detailed_teacher_courses.txt", "w", encoding="utf-8") as out:
    for f in files:
        if not f.endswith(".docx"):
            continue
        doc = docx.Document(os.path.join(h_dir, f))
        out.write(f"\n====================\nFILE: {f}\n")
        for i, p in enumerate(doc.paragraphs):
            t = p.text.strip()
            if "ข้าพเจ้า" in t or "รหัสวิชา" in t or "ประกอบด้วย" in t:
                out.write(f"P{i}: {t}\n")

print("Done details.")
