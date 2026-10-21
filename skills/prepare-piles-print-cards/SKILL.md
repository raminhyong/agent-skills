---
name: prepare-piles-print-cards
description: Prepare illustrated Piles character cards for printing by separating multi-card source sheets, preserving every complete outer frame including shared seam lines, normalizing cards to a supplied card-size reference, adding Thai character-name panels, arranging four portrait cards edge-to-edge on A4 landscape, and exporting a visually verified PDF. Use for Piles card sheets, character-card print layouts, frame-repair revisions, or requests to add names before A4 printing.
---

# Prepare Piles Print Cards

Create print-ready Piles character-card sheets without losing any part of the decorative frame.

## Required inputs

- Read every character source sheet that contains the card variants.
- Read the supplied `card size` reference and use its aspect ratio as the target for every card.
- Confirm the exact Thai character name from the filename or user-approved list.
- Inspect comparable approved output when available.

## Separate cards without damaging frames

1. Detect each card rectangle independently. Do not divide the source only at mathematical midpoints.
2. Detect the complete outer-frame cluster on all four sides before resizing. A frame may contain several parallel colored strokes.
3. Treat a detected line peak as the center of a frame cluster, not as the crop boundary. Search around the peak for the full continuous or near-continuous group of frame pixels, then crop at the outermost pixel of that group.
4. At a seam used by adjacent cards, give both cards a complete frame:
   - If two separate frame bands exist, assign the complete left band to the left card and the complete right band to the right card.
   - If one band is genuinely shared, include that entire band in both crops. Overlap the source crops as needed.
   - Never assign a shared line to only one card.
5. Use inclusive right and bottom bounds. When the image library uses exclusive crop endpoints, add one pixel after the detected final frame pixel.
6. Do not retain white gutters outside the frame. The crop should begin and end on the true outer edge of the frame.
7. Visually inspect every separated card at high resolution. Require an unbroken outer frame on the top, right, bottom, and left.

A practical detector may score dark, saturated pixels along rows and columns, find strong frame peaks, and expand each peak to the full nearby band. A starting threshold of roughly 40-50% of the peak score within a small local radius is useful, but always validate against the actual artwork.

## Normalize card size

1. Finish the frame-safe crop first.
2. Measure the cropped proportions and compare them with the supplied `card size` reference.
3. Resize every card to exactly the same target width, height, and aspect ratio.
4. Do not crop away additional frame pixels merely to force the target ratio.

## Add the character name

- Place the name at the bottom of every card.
- **Thai Typography & Font Blacklist (กฎเหล็กฟอนต์ภาษาไทย)**:
  - ❌ **ห้ามใช้ฟอนต์ `Leelawadee UI` / `Leelawadee` (`LeelaUIb.ttf`, `Leelawad.ttf`, `LeelaUI.ttf`) โดยเด็ดขาด**: ฟอนต์นี้มีปัญหาสระด้านบน (ิ, ี, ึ, ื, ั) กับวรรณยุกต์ (่, ้, ๊, ๋) ชนและทับซ้อนกันอย่างรุนแรง เช่น คำว่า "เล่าปี่", "เตียวเลี้ยว", "พระเจ้าเหี้ยนเต้"
  - ❌ **ห้ามเรนเดอร์ภาษาไทยด้วย PIL/Pillow `ImageFont.truetype()` แบบปกติโดยตรง**: เพราะขาด HarfBuzz OpenType GPOS shaping ทำให้สระกับวรรณยุกต์ไม่แยกชั้น
  - ✅ **ต้องเรนเดอร์ผ่าน Engine ที่รองรับ HarfBuzz / GPOS Mark-to-Mark**: เช่น Headless Chrome rasterizer (`text-rendering: geometricPrecision`) หรือ HarfBuzz shaping engine เพื่อให้วรรณยุกต์ลอยตัวเหนือสระบนอย่างถูกต้อง สวยงาม คมชัด 100%
- Keep the text panel inside the decorative frame. Detect the safe inner width instead of using the full card width.
- Leave approximately 2 mm between the panel and the lower card edge.
- Use no outline around the panel.
- Choose a panel color from the same color family as the card.
- Fade the panel gradually from stronger color at the bottom to transparent toward the top.
- Center the name and keep it legible without touching the frame.

## Arrange the print sheet

- **กระดาษ**: A4 แนวนอน (Landscape: 297 x 210 มม.)
- **ขนาดการ์ดมาตรฐาน**: สูง 98.0 มม. x กว้าง 68.98 มม. (สัดส่วน 518:736)
- **การจัดวางแบบจับคู่หน้า-หลัง (Paired Fold-and-Cut)**:
  - **รูปแบบซ้าย-ขวา (Left-Right Pairing)**:
    - 1 แผ่น บรรจุ 4 คู่ (8 ใบ = 4 คอลัมน์ x 2 แถว) ครบ 4 ท่าทางของ 1 ตัวละครใน 1 หน้า A4
    - แถวบน: ท่าที่ 1 [หน้า | หลัง] | ท่าที่ 2 [หน้า | หลัง]
    - แถวล่าง: ท่าที่ 3 [หน้า | หลัง] | ท่าที่ 4 [หน้า | หลัง]
    - **ทิศทางหลังไพ่ (Back Cover)**: วางหัวตั้งตรงปกติ (0° Rotation) ไม่ต้องกลับหัว 180° เพราะเมื่อพับประกบตามแนวตั้ง (ซ้าย-ขวา) ด้านหลังจะตั้งตรงสวยงามทันที
    - **เส้นนำและมาร์ก**:
      - กึ่งกลางระหว่างหน้า-หลังของแต่ละคู่: ตีเส้นประบอกรอยพับแนวตั้ง (Dashed Fold Line)
      - กึ่งกลางแผ่นระหว่างแถวบน-ล่าง และระหว่างคู่ซ้าย-ขวา: เส้นทึบสำหรับตัด (Cut Line)
      - มี Crop Marks ขอบนอกนำสายตาสำหรับการตัด 100% Actual Size
  - **ระยะขอบปลอดภัย**: ซ้าย-ขวา 10.54 มม., บน-ล่าง 7.00 มม. พิมพ์ได้สบายไม่ตกขอบเครื่องพิมพ์
- วางการ์ดชิดกันแบบไร้ช่องว่าง (0 Gap) และรักษาเส้นกรอบนอกของการ์ดครบถ้วน 100%

## Export and verify

1. Save high-resolution page images as intermediates when useful.
2. Export the final result as an A4 landscape PDF without fit-to-page scaling or added crop marks.
3. Render every changed PDF page back to PNG.
4. Inspect at high resolution for:
   - complete outer frames on all four sides of every card
   - full frames at every card-to-card seam
   - equal card sizes and proportions
   - no gaps between cards
   - name panels that do not cover the frame
   - correct Thai spelling and mark placement
5. During a revision, change only the named characters or defective crop bounds. Preserve all already-approved pages and styling.

Do not deliver until the rendered PDF passes every check.
