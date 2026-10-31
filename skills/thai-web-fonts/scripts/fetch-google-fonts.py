#!/usr/bin/env python3
"""ดึงฟอนต์ไทยจาก Google Fonts เป็น woff2 (subset thai + latin) มาเก็บในโปรเจกต์

ใช้:  python fetch-google-fonts.py <project-root> [out-dir]
เช่น: python fetch-google-fonts.py C:/Users/me/repos/myapp

ได้ผลลัพธ์:
  <project>/public/fonts/<slug>/<slug>-<weight>-<subset>.woff2
  <project>/public/fonts/manifest.json   (ใช้ต่อกับ make-font-css)
"""
import os, re, json, sys, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

FAMILIES = {
    "Kanit": [400, 500, 600, 700],
    "Prompt": [400, 500, 600, 700],
    "Mitr": [400, 500, 600],
    "IBM Plex Sans Thai": [400, 500, 600, 700],
    "Sarabun": [400, 500, 600, 700],
    "Taviraj": [400, 500, 600, 700],
    "Anuphan": [400, 500, 600, 700],
    "Chonburi": [400],
    "Trirong": [400, 500, 600, 700],
}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "public", "fonts")
    os.makedirs(out, exist_ok=True)

    manifest = []
    for family, weights in FAMILIES.items():
        w = ";".join(str(x) for x in weights)
        api = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@{w}&display=swap"
        css = fetch(api).decode("utf-8")
        blocks = re.findall(r"/\*\s*([a-z\-]+)\s*\*/\s*@font-face\s*\{([^}]+)\}", css)
        fam_dir = os.path.join(out, slug(family))
        os.makedirs(fam_dir, exist_ok=True)
        faces = []
        for subset, body in blocks:
            if subset not in ("thai", "latin"):
                continue
            weight = re.search(r"font-weight:\s*(\d+)", body)
            src = re.search(r"url\((https://[^)]+\.woff2)\)", body)
            ur = re.search(r"unicode-range:\s*([^;]+);", body)
            if not (weight and src):
                continue
            fname = f"{slug(family)}-{weight.group(1)}-{subset}.woff2"
            path = os.path.join(fam_dir, fname)
            if not os.path.exists(path):
                with open(path, "wb") as f:
                    f.write(fetch(src.group(1)))
            faces.append({
                "subset": subset,
                "weight": weight.group(1),
                "file": f"{slug(family)}/{fname}",
                "unicodeRange": ur.group(1).strip() if ur else None,
                "size": os.path.getsize(path),
            })
        manifest.append({"family": family, "faces": faces})
        thai = [f["size"] for f in faces if f["subset"] == "thai"]
        print(f"{family:20s} faces={len(faces):2d} thai={sum(thai)//1024 if thai else 0}KB")

    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    total = sum(f["size"] for m in manifest for f in m["faces"])
    print(f"TOTAL {total/1024/1024:.2f} MB -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
