#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subject Saliency & Bounding Box Detection Engine
Uses local BRIA-RMBG SOTA ONNX model to extract foreground mask,
calculate exact bounding box (X/Y min-max percentages), and recommend safe layout zones.
"""

import os
import sys
import numpy as np
from PIL import Image
import onnxruntime as ort

MODEL_PATH = r"C:\Users\patti\.rembg\models\bria-rmbg\bria-rmbg.onnx"

def detect_subject_bbox(image_path: str, model_path: str = MODEL_PATH):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"ONNX Model not found: {model_path}")

    orig_img = Image.open(image_path).convert("RGB")
    w, h = orig_img.size

    input_size = (1024, 1024)
    resized_img = orig_img.resize(input_size, Image.Resampling.BILINEAR)
    img_data = np.array(resized_img, dtype=np.float32) / 255.0
    img_data = (img_data - 0.5) / 1.0
    img_data = img_data.transpose((2, 0, 1))
    img_data = np.expand_dims(img_data, axis=0)

    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    res = session.run([output_name], {input_name: img_data})
    alpha = res[0][0, 0]

    alpha_img = Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8))
    alpha_orig = alpha_img.resize((w, h), Image.Resampling.BILINEAR)
    alpha_np = np.array(alpha_orig)

    foreground_mask = alpha_np > 30
    coords = np.argwhere(foreground_mask)
    if coords.size == 0:
        return None

    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    result = {
        "image_size": {"width": w, "height": h},
        "bbox_pixels": {"x_min": int(x_min), "x_max": int(x_max), "y_min": int(y_min), "y_max": int(y_max)},
        "bbox_percent": {
            "x_min": round(x_min / w * 100, 2),
            "x_max": round(x_max / w * 100, 2),
            "y_min": round(y_min / h * 100, 2),
            "y_max": round(y_max / h * 100, 2),
        },
        "subject_dimensions": {
            "width_percent": round((x_max - x_min) / w * 100, 2),
            "height_percent": round((y_max - y_min) / h * 100, 2),
        },
        "focal_center": {
            "x_percent": round((x_min + x_max) / 2 / w * 100, 2),
            "y_percent": round((y_min + y_max) / 2 / h * 100, 2),
        },
        "safe_mask_zones": {
            "top_fade_limit_percent": round(max(0, y_min / h * 100 - 3), 2),
            "bottom_fade_limit_percent": round(min(100, y_max / h * 100 + 3), 2),
        }
    }
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = r"C:\Users\patti\Box\AGENT SKILLS\slides\assets\chicken_gem_proverb.png"
    res = detect_subject_bbox(target)
    import json
    print(json.dumps(res, indent=2))

