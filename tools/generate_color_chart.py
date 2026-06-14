#!/usr/bin/env python3
"""Generate a comprehensive color test chart for LUT visual analysis."""

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 1000
img = Image.new('RGB', (W, H), (40, 40, 40))
draw = ImageDraw.Draw(img)

def rect(x, y, w, h, color):
    draw.rectangle([x, y, x+w-1, y+h-1], fill=color, outline=(80,80,80))

def label(x, y, text, color=(200,200,200)):
    try:
        draw.text((x, y), text, fill=color)
    except:
        pass

# ===== Row 1: MacBeth-style 24 patches (approximate sRGB values) =====
macbeth = [
    # Row 1: dark skin, light skin, blue sky, foliage, blue flower, bluish green
    [(115, 82, 68), "DSkin"], [(194,150,130), "LSkin"], [(98,122,157), "Sky"],
    [(87,108,67), "Leaf"], [(133,128,177), "BFlr"], [(103,189,170), "BGrn"],
    # Row 2: orange, purplish blue, moderate red, purple, yellow green, orange yellow
    [(214,126,44), "Org"], [(80,91,166), "PBlu"], [(193,90,99), "Red"],
    [(94,60,108), "Purp"], [(157,188,64), "YGrn"], [(224,163,46), "OYel"],
    # Row 3: blue, green, red, yellow, magenta, cyan
    [(56,61,150), "Blue"], [(70,148,73), "Grn"], [(175,54,60), "Red2"],
    [(231,199,31), "Yel"], [(187,86,149), "Mag"], [(8,133,161), "Cyan"],
    # Row 4: white, neutral8, neutral6.5, neutral5, neutral3.5, black
    [(243,243,242), "Wht"], [(200,200,200), "N8"], [(160,160,160), "N6.5"],
    [(122,122,121), "N5"], [(85,85,85), "N3.5"], [(52,52,52), "Blk"],
]

PATCH = 60
GAP = 6
for row in range(4):
    for col in range(6):
        idx = row * 6 + col
        x = 10 + col * (PATCH + GAP)
        y = 10 + row * (PATCH + GAP + 14)
        rect(x, y, PATCH, PATCH, macbeth[idx][0])
        label(x, y+PATCH+2, macbeth[idx][1], (180,180,180))

# ===== Row 2: Skin tone gradient =====
label(10, 290, "Skin tones:", (220,220,220))
skin_tones = [
    (240, 200, 170),  # Very light
    (225, 185, 150),
    (210, 170, 135),
    (195, 155, 120),
    (180, 140, 105),
    (165, 125, 90),
    (150, 110, 75),   # Dark
]
for i, st in enumerate(skin_tones):
    x = 10 + i * (PATCH + GAP)
    rect(x, 310, PATCH, 50, st)

# ===== Row 3: Blue sky gradient =====
label(10, 375, "Blue sky gradient:", (220,220,220))
for i in range(8):
    t = i / 7.0
    r = int(30 + t * 40)
    g = int(80 + t * 80)
    b = int(180 + t * 75)
    x = 10 + i * (PATCH + GAP)
    rect(x, 395, PATCH, 50, (r, g, b))

# ===== Row 4: Green foliage gradient =====
label(10, 460, "Green foliage gradient:", (220,220,220))
for i in range(8):
    t = i / 7.0
    r = int(20 + t * 50)
    g = int(60 + t * 120)
    b = int(15 + t * 30)
    x = 10 + i * (PATCH + GAP)
    rect(x, 480, PATCH, 50, (r, g, b))

# ===== Row 5: Red→Orange→Yellow gradient =====
label(10, 545, "Red → Orange → Yellow:", (220,220,220))
for i in range(12):
    t = i / 11.0
    r = 255
    g = int(t * 255)
    b = int((1 - abs(t - 0.5) * 2) * 80)
    x = 10 + i * (52 + 4)
    rect(x, 565, 52, 50, (r, g, b))

# ===== Row 6: Grayscale ramp =====
label(10, 630, "Grayscale ramp:", (220,220,220))
for i in range(16):
    v = int(i / 15.0 * 255)
    x = 10 + i * (PATCH // 2 + 2)
    rect(x, 650, PATCH // 2, 50, (v, v, v))

# ===== Row 7: Pure primaries/secondaries =====
label(10, 715, "Pure colors:", (220,220,220))
pure = [
    ((255,0,0), "R"), ((255,128,0), "Or"), ((255,255,0), "Y"),
    ((0,255,0), "G"), ((0,255,255), "C"), ((0,0,255), "B"),
    ((128,0,255), "V"), ((255,0,255), "M"),
]
for i, (col, name) in enumerate(pure):
    x = 10 + i * (PATCH + GAP)
    rect(x, 735, PATCH, 50, col)
    label(x, 735+PATCH, name, (200,200,200))

# ===== Save =====
out_path = 'output/test_color_chart.png'
img.save(out_path)
print(f"Saved: {out_path}")
