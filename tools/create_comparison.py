#!/usr/bin/env python3
"""Create before/after comparison images with analysis annotations."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_comparison(before_path, after_path, output_path, label_before="Original", label_after="Gold 200 LUT"):
    before = Image.open(before_path)
    after = Image.open(after_path)
    
    # Resize for manageable comparison
    max_w = 1200
    if before.width > max_w:
        ratio = max_w / before.width
        before = before.resize((max_w, int(before.height * ratio)), Image.LANCZOS)
        after = after.resize((max_w, int(after.height * ratio)), Image.LANCZOS)
    
    w, h = before.size
    # Stack vertically with labels
    combined = Image.new('RGB', (w + 4, h * 2 + 50), (30, 30, 30))
    draw = ImageDraw.Draw(combined)
    
    combined.paste(before, (2, 25))
    combined.paste(after, (2, h + 30))
    
    # Labels
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font = ImageFont.load_default()
    draw.text((10, 5), label_before, fill=(255, 255, 255), font=font)
    draw.text((10, h + 8), label_after, fill=(255, 200, 50), font=font)
    
    combined.save(output_path)
    print(f"Saved: {output_path}")

# Chart comparison
create_comparison('output/test_color_chart.png', 'output/test_color_chart_gold200.png', 'output/comparison_chart.png',
                  "Original Test Chart (sRGB)", "Gold 200 LUT Applied")

print("Done!")
