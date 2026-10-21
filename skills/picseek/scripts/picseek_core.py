#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PicSeek Core Engine
Targeted image and evidence mining using PyThaiNLP tokenization,
weighted relevance scoring, and automatic report slot fulfillment.
"""

import os
import sys
import argparse
import json
import shutil
import re
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageOps

try:
    from pythainlp.tokenize import word_tokenize
    HAS_PYTHAINLP = True
except ImportError:
    HAS_PYTHAINLP = False

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

def tokenize_thai(text: str) -> list[str]:
    """Tokenize Thai text safely using PyThaiNLP newmm engine."""
    if not text:
        return []
    clean_text = re.sub(r"[_\-\.\/\\]", " ", text)
    if HAS_PYTHAINLP:
        raw_tokens = word_tokenize(clean_text, engine="newmm")
    else:
        raw_tokens = clean_text.split()
    tokens = [t.strip().lower() for t in raw_tokens if len(t.strip()) > 1]
    return tokens

def calculate_relevance_score(image_path: Path, search_root: Path, query: str, query_tokens: list[str]) -> tuple[float, list[str]]:
    """
    Score image relevance based on path tokens, exact match, and numbers.
    Returns (score, matched_keywords).
    """
    rel_path_str = str(image_path.relative_to(search_root))
    path_tokens = set(tokenize_thai(rel_path_str))
    
    score = 0.0
    matched = []
    
    # 1. Exact query match in full relative path
    clean_query = query.strip().lower()
    clean_path = rel_path_str.lower()
    if clean_query and clean_query in clean_path:
        score += 50.0
        matched.append(clean_query)
        
    # 2. Token overlap score
    for q_tok in query_tokens:
        if q_tok in path_tokens:
            score += 15.0
            matched.append(q_tok)
        elif any(q_tok in p_tok for p_tok in path_tokens):
            score += 7.0
            matched.append(q_tok)
            
    # 3. Numeric / Policy number matching (e.g. 14-2569, 13-01, 2569)
    query_numbers = re.findall(r"\d+", query)
    path_numbers = re.findall(r"\d+", rel_path_str)
    for num in query_numbers:
        if num in path_numbers:
            score += 12.0
            matched.append(num)
            
    # 4. Bonus for specific educational evidence keywords
    edu_keywords = ["โครงการ", "กิจกรรม", "อบรม", "เกียรติบัตร", "คำสั่ง", "รายงาน", "นิทรรศน์", "รางวัล", "ประกวด"]
    for kw in edu_keywords:
        if kw in query_tokens and kw in path_tokens:
            score += 10.0
            
    return score, list(set(matched))

def scan_and_rank_images(folder_path: str, query: str, top_k: int = 5) -> list[dict]:
    """Scan folder and return ranked images matching the query."""
    root = Path(folder_path).resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
        
    query_tokens = tokenize_thai(query)
    candidates = []
    
    for dirpath, _, filenames in os.walk(root):
        d_path = Path(dirpath)
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in IMAGE_EXTENSIONS:
                img_path = d_path / fname
                score, matched = calculate_relevance_score(img_path, root, query, query_tokens)
                if score > 0:
                    candidates.append({
                        "path": str(img_path),
                        "filename": fname,
                        "relative_path": str(img_path.relative_to(root)),
                        "score": round(score, 2),
                        "matched_tokens": matched,
                        "file_size": img_path.stat().st_size
                    })
                    
    # Sort candidates by score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]

def copy_and_sanitize_image(src_path: str, dest_dir: str, slot_name: str) -> str:
    """Copy image to target slot and sanitize EXIF/orientation."""
    dest_path_dir = Path(dest_dir).resolve()
    dest_path_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(src_path).suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        ext = ".jpg"
        
    out_file = dest_path_dir / f"{slot_name}{ext}"
    
    # Sanitize and transpose with Pillow to prevent EXIF division-by-zero
    try:
        with Image.open(src_path) as im:
            im = ImageOps.exif_transpose(im)
            if ext in [".jpg", ".jpeg"]:
                im = im.convert("RGB")
                im.save(out_file, format="JPEG", quality=95)
            else:
                im.save(out_file, format="PNG")
    except Exception:
        shutil.copy2(src_path, out_file)
        
    return str(out_file)

def main():
    parser = argparse.ArgumentParser(description="PicSeek: Targeted Photo & Evidence Mining Engine")
    parser.add_argument("path", help="Folder path to search within")
    parser.add_argument("query", help="Thai/English search query or indicator context")
    parser.add_argument("--top", type=int, default=5, help="Number of top results to return")
    parser.add_argument("--slot", type=str, default="", help="Target slot code (e.g. 13-01-01)")
    parser.add_argument("--dest-dir", type=str, default="", help="Destination evidence directory")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    
    args = parser.parse_args()
    
    try:
        results = scan_and_rank_images(args.path, args.query, top_k=args.top)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
        
    copied_path = None
    if args.slot and args.dest_dir and results:
        best_match = results[0]["path"]
        copied_path = copy_and_sanitize_image(best_match, args.dest_dir, args.slot)
        
    if args.json:
        output_payload = {
            "query": args.query,
            "search_path": args.path,
            "total_found": len(results),
            "results": results,
            "fulfilled_slot": args.slot if copied_path else None,
            "copied_path": copied_path
        }
        print(json.dumps(output_payload, ensure_ascii=False, indent=2))
        return
        
    print(f"\n🔍 PicSeek Search Results for: '{args.query}'")
    print(f"📂 Folder: {args.path}")
    print("=" * 80)
    
    if not results:
        print("❌ ไม่พบรูปภาพที่สอดคล้องกับคำค้นหาในโฟลเดอร์นี้")
        return
        
    for idx, r in enumerate(results, 1):
        print(f"[{idx}] ความตรง: {r['score']:.1f} คะแนน | ไฟล์: {r['filename']}")
        print(f"    เส้นทาง: {r['relative_path']}")
        print(f"    คำสำคัญที่พบ: {', '.join(r['matched_tokens'])}")
        print(f"    ขนาด: {r['file_size'] / 1024:.1f} KB")
        print("-" * 80)
        
    if copied_path:
        print(f"✅ บันทึกภาพอันดับ 1 ลงสล็อต {args.slot} เรียบร้อยแล้ว:")
        print(f"   -> {copied_path}\n")

if __name__ == "__main__":
    main()
