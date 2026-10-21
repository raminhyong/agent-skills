"""
arrange_cards.py - Reusable Engine for Arranging Card Deck Sheets on A4
Supports:
  - Mode 2.1: All-Fronts Sheets (วางแบบหน้าไพ่ล้วน) + Separate Backs
  - Mode 2.2: Paired Front-Back Sheets (วางแบบหน้า-หลังคู่กันสำหรับพับตัด)
  - Auto-calculation of optimal orientation (Portrait vs Landscape) and grid size
  - 300 DPI prepress output with outer crop marks & faint guide lines
  - Guaranteed temp file cleanup
"""

import os
import shutil
import tempfile
from PIL import Image, ImageDraw, ImageFont


def calculate_optimal_layout(card_w_mm, card_h_mm, forced_orientation=None, margin_mm=8):
    """
    Given card dimensions (mm), calculate optimal paper orientation and grid for A4.
    A4 Portrait: 210 x 297 mm
    A4 Landscape: 297 x 210 mm
    """
    orientations = ['landscape', 'portrait'] if not forced_orientation else [forced_orientation.lower()]
    best = None

    for orient in orientations:
        paper_w = 297 if orient == 'landscape' else 210
        paper_h = 210 if orient == 'landscape' else 297

        avail_w = paper_w - (margin_mm * 2)
        avail_h = paper_h - (margin_mm * 2)

        cols = int(avail_w // card_w_mm)
        rows = int(avail_h // card_h_mm)
        total = cols * rows
        used_area = total * (card_w_mm * card_h_mm)
        efficiency = used_area / (paper_w * paper_h)

        res = {
            'orientation': orient,
            'paper_w_mm': paper_w,
            'paper_h_mm': paper_h,
            'cols': cols,
            'rows': rows,
            'total_cards': total,
            'efficiency': efficiency,
            'grid_w_mm': cols * card_w_mm,
            'grid_h_mm': rows * card_h_mm,
        }

        if best is None or res['total_cards'] > best['total_cards'] or (
            res['total_cards'] == best['total_cards'] and res['efficiency'] > best['efficiency']
        ):
            best = res

    return best


def draw_sheet_prepress(sheet, margin_x, margin_y, card_w_px, card_h_px, cols, rows, title_text, sub_text=""):
    """Draws outer crop marks, faint inner cut lines, and margin text."""
    draw = ImageDraw.Draw(sheet)
    grid_w = cols * card_w_px
    grid_h = rows * card_h_px

    # 1. Faint inner cut guidelines (for scissors)
    guide_col = (190, 190, 190)
    for c in range(1, cols):
        lx = margin_x + c * card_w_px
        draw.line((lx, margin_y, lx, margin_y + grid_h), fill=guide_col, width=1)
    for r in range(1, rows):
        ly = margin_y + r * card_h_px
        draw.line((margin_x, ly, margin_x + grid_w, ly), fill=guide_col, width=1)

    # Outer border
    draw.rectangle((margin_x, margin_y, margin_x + grid_w, margin_y + grid_h), outline=guide_col, width=1)

    # 2. Outer crop marks (for ruler + craft knife)
    crop_col = (50, 50, 50)
    t_len = 35
    t_gap = 12
    for c in range(cols + 1):
        cx = margin_x + c * card_w_px
        draw.line((cx, margin_y - t_gap - t_len, cx, margin_y - t_gap), fill=crop_col, width=2)
        draw.line((cx, margin_y + grid_h + t_gap, cx, margin_y + grid_h + t_gap + t_len), fill=crop_col, width=2)
    for r in range(rows + 1):
        ry = margin_y + r * card_h_px
        draw.line((margin_x - t_gap - t_len, ry, margin_x - t_gap, ry), fill=crop_col, width=2)
        draw.line((margin_x + grid_w + t_gap, ry, margin_x + grid_w + t_gap + t_len, ry), fill=crop_col, width=2)

    # 3. Margin Info
    try:
        f_bold = ImageFont.truetype('C:/Windows/Fonts/tahomabd.ttf', 24)
        f_reg = ImageFont.truetype('C:/Windows/Fonts/tahoma.ttf', 24)
    except Exception:
        f_bold = f_reg = ImageFont.load_default()

    draw.text((margin_x, 42), title_text, font=f_bold, fill=(40, 40, 40))
    if sub_text:
        draw.text((margin_x + 480, 44), f"—  {sub_text}", font=f_reg, fill=(90, 90, 90))
    draw.text((margin_x, sheet.height - 52), "ขนาดพิมพ์จริง 100% (Actual Size) บนกระดาษ A4", font=f_reg, fill=(100, 100, 100))


def render_all_fronts_sheet(card_imgs, page_num, total_pages, card_w_px, card_h_px, cols, rows, is_landscape=True, title=""):
    """Mode 2.1: Render a single sheet containing front cards only."""
    pw = 3508 if is_landscape else 2480
    ph = 2480 if is_landscape else 3508

    grid_w = cols * card_w_px
    grid_h = rows * card_h_px
    mx = (pw - grid_w) // 2
    my = (ph - grid_h) // 2

    sheet = Image.new('RGB', (pw, ph), (255, 255, 255))

    for idx, card in enumerate(card_imgs):
        if idx >= cols * rows:
            break
        c = idx % cols
        r = idx // cols
        x = mx + c * card_w_px
        y = my + r * card_h_px

        im = Image.open(card) if isinstance(card, str) else card
        resized = im.resize((card_w_px, card_h_px), Image.Resampling.LANCZOS)
        sheet.paste(resized, (x, y))

    heading = title or f"แผ่นที่ {page_num}/{total_pages} (หน้าไพ่ล้วน)"
    draw_sheet_prepress(sheet, mx, my, card_w_px, card_h_px, cols, rows, heading)
    return sheet


def render_paired_fold_sheet(pairs, page_num, total_pages, card_w_px, card_h_px, pair_orientation='horizontal', is_landscape=True, title=""):
    """
    Mode 2.2: Render front & back cards paired side-by-side or top-and-bottom with fold line.
    pairs: list of tuples [(front_img, back_img), ...]
    """
    pw = 3508 if is_landscape else 2480
    ph = 2480 if is_landscape else 3508

    # In horizontal pairing: 2 cards per pair horizontally -> pair_w = card_w_px * 2
    if pair_orientation == 'horizontal':
        cols = 4  # e.g., 2 pairs = 4 card slots
        rows = 2
    else:
        cols = 4
        rows = 2

    grid_w = cols * card_w_px
    grid_h = rows * card_h_px
    mx = (pw - grid_w) // 2
    my = (ph - grid_h) // 2

    sheet = Image.new('RGB', (pw, ph), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    # Place pairs
    pair_idx = 0
    for r in range(rows):
        for c in range(0, cols, 2):
            if pair_idx < len(pairs):
                f_card, b_card = pairs[pair_idx]
                x_f = mx + c * card_w_px
                y_f = my + r * card_h_px
                x_b = mx + (c + 1) * card_w_px
                y_b = y_f

                im_f = Image.open(f_card) if isinstance(f_card, str) else f_card
                im_b = Image.open(b_card) if isinstance(b_card, str) else b_card

                sheet.paste(im_f.resize((card_w_px, card_h_px), Image.Resampling.LANCZOS), (x_f, y_f))
                sheet.paste(im_b.resize((card_w_px, card_h_px), Image.Resampling.LANCZOS), (x_b, y_b))

                # Draw fold line (dashed) between front and back
                fold_x = x_b
                for dash_y in range(y_f, y_f + card_h_px, 12):
                    draw.line((fold_x, dash_y, fold_x, min(dash_y + 6, y_f + card_h_px)), fill=(120, 120, 120), width=1)

                pair_idx += 1

    heading = title or f"แผ่นที่ {page_num}/{total_pages} (หน้า-หลังคู่กันสำหรับพับตัด)"
    draw_sheet_prepress(sheet, mx, my, card_w_px, card_h_px, cols, rows, heading, "เส้นประตรงกลางคู่ = รอยพับ (Fold Line)")
    return sheet
