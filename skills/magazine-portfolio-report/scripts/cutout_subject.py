#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Subject Cutout & Background Removal Engine (Zero External Dependencies)
Uses local BRIA-RMBG SOTA ONNX model via onnxruntime to extract pristine transparent PNG/WebP assets.
"""

import os
import sys
import argparse
import numpy as np
from PIL import Image
import onnxruntime as ort

MODEL_PATH = r"C:\Users\patti\.rembg\models\bria-rmbg\bria-rmbg.onnx"

def remove_background(input_path: str, output_path: str, trim: bool = False, model_path: str = MODEL_PATH):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Image not found: {input_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"ONNX Model not found: {model_path}")

    print(f"Loading image: {input_path}")
    orig_img = Image.open(input_path).convert("RGB")
    w, h = orig_img.size

    input_size = (1024, 1024)
    resized_img = orig_img.resize(input_size, Image.Resampling.BILINEAR)
    img_data = np.array(resized_img, dtype=np.float32) / 255.0
    img_data = (img_data - 0.5) / 1.0
    img_data = img_data.transpose((2, 0, 1))
    img_data = np.expand_dims(img_data, axis=0)

    print("Running BRIA-RMBG ONNX inference...")
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    res = session.run([output_name], {input_name: img_data})
    alpha = res[0][0, 0]

    # Convert alpha mask to 0-255 image
    alpha_img = Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8))
    alpha_orig = alpha_img.resize((w, h), Image.Resampling.BILINEAR)

    # Create transparent RGBA image
    cutout = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cutout.paste(orig_img, (0, 0), alpha_orig)

    if trim:
        bbox = cutout.getbbox()
        if bbox:
            cutout = cutout.crop(bbox)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cutout.save(output_path)
    print(f"Saved transparent cutout to: {output_path} ({cutout.width}x{cutout.height})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BRIA-RMBG AI Cutout Tool")
    parser.add_argument("input", help="Path to input image")
    parser.add_argument("output", help="Path to output PNG/WebP image")
    parser.add_argument("--trim", action="store_true", help="Trim transparent borders")
    args = parser.parse_args()
    
    remove_background(args.input, args.output, trim=args.trim)
