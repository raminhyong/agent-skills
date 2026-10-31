# legacy/ — คลังสคริปต์งานข้อสอบ (ไม่ใช่ทางหลัก)

สคริปต์ 1 งาน/1 ไฟล์ (Job01–Job03) ที่ใช้จริงตอนจัดรูปเล่มข้อสอบ เก็บไว้เป็นแหล่งอ้างอิงโค้ด
**ไม่ต้องโหลดทั้งหมด** — ทางหลักคือ `../format_job03_example.py` + `references/format-spec-full.md`

กลุ่มที่ควรรู้จัก

- `parse_new_job02.py`, `build_balanced_job02.py`, `refine_balanced_choices.py` — แยกข้อสอบเก่า → จัดสมดุลความยาวตัวเลือก
- `format_job02.py` — ฟอร์แมตเตอร์อีกรุ่น (โครงสร้างเดียวกับ job03)
- `verify_job0*.py`, `check_*.py`, `measure_*.py`, `count_q_per_page.py` — ตรวจผลหลังฟอร์แมต
- `inspect_*.py`, `print_*.py` — เครื่องมือสำรวจ/ดีบัก XML ของ docx

ไฟล์ข้อมูลที่ใช้ร่วม (Job02/03 .json, .docx) อยู่ใน `../../examples/`
