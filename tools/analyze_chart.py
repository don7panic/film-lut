#!/usr/bin/env python3
"""Quantitative color analysis of gold200 LUT on test chart patches."""
import numpy as np
from PIL import Image

# Load before and after
before = np.array(Image.open('output/test_color_chart.png'), dtype=np.float64) / 255.0
after = np.array(Image.open('output/test_color_chart_gold200.png'), dtype=np.float64) / 255.0

def rgb_to_hsl_px(r, g, b):
    mx = max(r, g, b)
    mn = min(r, g, b)
    l = (mx + mn) / 2.0
    delta = mx - mn
    if delta == 0:
        s = 0.0
        h = 0.0
    else:
        s = delta / (mx + mn) if l < 0.5 else delta / (2.0 - mx - mn)
        if mx == r:
            h = 60.0 * (((g - b) / delta) % 6.0)
        elif mx == g:
            h = 60.0 * (((b - r) / delta) + 2.0)
        else:
            h = 60.0 * (((r - g) / delta) + 4.0)
    return h, s, l

PATCH = 60
GAP = 6
macbeth_names = [
    "DarkSkin","LightSkin","BlueSky","Foliage","BlueFlower","BGrn",
    "Orange","PBlue","Red","Purple","YGrn","OYel",
    "Blue","Green","Red2","Yellow","Magenta","Cyan",
    "White","N8","N6.5","N5","N3.5","Black",
]

print("=" * 90)
print(f"{'Patch':<12} {'Before RGB':<22} {'After RGB':<22} {'ΔHue':<8} {'ΔSat':<8} {'ΔLum':<8} {'Note'}")
print("=" * 90)

for row in range(4):
    for col in range(6):
        idx = row * 6 + col
        x = 10 + col * (PATCH + GAP) + PATCH // 2
        y = 10 + row * (PATCH + GAP + 14) + PATCH // 2
        
        br, bg, bb = before[y, x]
        ar, ag, ab = after[y, x]
        
        bh, bs, bl = rgb_to_hsl_px(br, bg, bb)
        ah, as_, al = rgb_to_hsl_px(ar, ag, ab)
        
        dh = ah - bh
        ds = as_ - bs
        dl = al - bl
        
        # Detect issues
        notes = []
        if abs(dh) > 5:
            notes.append(f"HUE SHIFT {dh:+.0f}°")
        if ds < -0.15:
            notes.append(f"DESAT {ds:+.0%}")
        if ds > 0.15:
            notes.append(f"SAT+{ds:+.0%}")
        if dl > 0.1:
            notes.append(f"LIFT+{dl:+.0%}")
        if dl < -0.1:
            notes.append(f"DARK{dl:+.0%}")
        
        before_str = f"({int(br*255):3d},{int(bg*255):3d},{int(bb*255):3d})"
        after_str = f"({int(ar*255):3d},{int(ag*255):3d},{int(ab*255):3d})"
        note_str = " | ".join(notes) if notes else ""
        print(f"{macbeth_names[idx]:<12} {before_str:<22} {after_str:<22} {dh:+7.1f}° {ds:+7.1%} {dl:+7.1%}  {note_str}")

# Analyze grayscale ramp
print("\n" + "=" * 90)
print("GRAYSCALE RAMP ANALYSIS")
print("=" * 90)
print(f"{'Level':<8} {'Before':<12} {'After':<12} {'R/G/B Ratio After':<22} {'Warm cast?'}")
for i in range(16):
    x = 10 + i * (PATCH // 2 + 2) + PATCH // 4
    y = 650 + 25
    br, bg, bb = before[y, x]
    ar, ag, ab = after[y, x]
    ratio = f"R={ar/max(ag,0.01):.3f} G=1.000 B={ab/max(ag,0.01):.3f}"
    warm = "WARM ✓" if ar > ag * 1.03 else ("COOL" if ab > ag * 1.03 else "OK")
    print(f"  V={int(br*255):3d}   ({int(br*255):3d},{int(bg*255):3d},{int(bb*255):3d}) ({int(ar*255):3d},{int(ag*255):3d},{int(ab*255):3d})  {ratio:<22} {warm}")

# Skin tone gradient
print("\n" + "=" * 90)
print("SKIN TONE GRADIENT")
print("=" * 90)
for i in range(7):
    x = 10 + i * (PATCH + GAP) + PATCH // 2
    y = 310 + 25
    br, bg, bb = before[y, x]
    ar, ag, ab = after[y, x]
    bh, bs, bl = rgb_to_hsl_px(br, bg, bb)
    ah, as_, al = rgb_to_hsl_px(ar, ag, ab)
    print(f"  {i+1}: ({int(br*255)},{int(bg*255)},{int(bb*255)}) H={bh:.0f}° -> ({int(ar*255)},{int(ag*255)},{int(ab*255)}) H={ah:.0f}° ΔH={ah-bh:+.0f}° ΔS={as_-bs:+.0%}")

# Blue sky gradient
print("\n" + "=" * 90)
print("BLUE SKY GRADIENT")
print("=" * 90)
for i in range(8):
    x = 10 + i * (PATCH + GAP) + PATCH // 2
    y = 395 + 25
    br, bg, bb = before[y, x]
    ar, ag, ab = after[y, x]
    bh, bs, bl = rgb_to_hsl_px(br, bg, bb)
    ah, as_, al = rgb_to_hsl_px(ar, ag, ab)
    print(f"  {i+1}: ({int(br*255)},{int(bg*255)},{int(bb*255)}) H={bh:.0f}° -> ({int(ar*255)},{int(ag*255)},{int(ab*255)}) H={ah:.0f}° ΔH={ah-bh:+.0f}° ΔS={as_-bs:+.0%}")

print("\nDone!")
