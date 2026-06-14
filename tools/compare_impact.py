#!/usr/bin/env python3
"""对比修正前后 hassy_blue 的视觉冲击力"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.core import apply_tone_curve, apply_color_grade, linear_to_display, rgb_to_hsl, hsl_to_rgb
from engine.preset import load_preset

# 修正前参数（v1）
v1 = {
    'name': 'v1', 'title': 'v1',
    'tone': {
        'black_lift': 0.0012, 'shadow_toe_pivot': 0.10, 'shadow_toe_power': 0.80,
        'contrast': 0.95, 'per_channel_contrast': [1.00, 1.00, 1.00],
        'highlight_shoulder_start': 0.72, 'highlight_shoulder_power': 1.22,
    },
    'color': {
        'shadow_tint': [1.00, 1.00, 1.01], 'highlight_tint': [1.00, 1.00, 1.00],
        'global_saturation': 0.94, 'highlight_desat_start': 0.62, 'highlight_desat_max': 0.10,
        'skin_hue_min': 8.0, 'skin_hue_max': 42.0, 'skin_sat_adjust': 0.92,
        'teal_push': 0.0, 'orange_push': 0.0,
        'blue_saturation_boost': 1.05, 'blue_luminance_shift': -0.02, 'blue_hue_shift': 1.5,
        'white_balance_shift_k': -400.0,
    },
}

v2 = load_preset('hassy_blue')

def pipeline(rgb, p):
    toned = apply_tone_curve(rgb, p)
    graded = apply_color_grade(toned, p)
    return linear_to_display(graded)

# ── 中性灰对比 ──
print("=" * 60)
print("中性灰阶梯对比 (input → v1 → v2)")
print("=" * 60)
print(f"{'Input':>8} {'v1_avg':>8} {'v2_avg':>8} {'v1_B-R':>8} {'v2_B-R':>8}")
for lvl in [0.05, 0.18, 0.35, 0.50, 0.70, 0.85]:
    g = np.array([lvl]*3)
    o1 = pipeline(g, v1); o2 = pipeline(g, v2)
    print(f"{lvl:8.2f} {np.mean(o1):8.4f} {np.mean(o2):8.4f} {o1[2]-o1[0]:+8.4f} {o2[2]-o2[0]:+8.4f}")

# ── 关键色彩对比 ──
print(f"\n{'='*60}")
print("关键色彩对比 (input → v1 → v2)")
print("=" * 60)
tests = [
    ("Blue 240°", 240, 0.7, 0.5),
    ("Sky 210°",  210, 0.6, 0.6),
    ("Skin 25°",   25, 0.5, 0.5),
    ("Red 0°",      0, 0.7, 0.5),
    ("Green 120°",120, 0.7, 0.5),
]
for name, h, s, l in tests:
    r, g, b = hsl_to_rgb(np.array([float(h)]), np.array([float(s)]), np.array([float(l)]))
    rgb = np.array([float(r.item()), float(g.item()), float(b.item())])
    o1 = pipeline(rgb, v1); o2 = pipeline(rgb, v2)
    h1, s1, l1 = rgb_to_hsl(o1[0], o1[1], o1[2])
    h2, s2, l2 = rgb_to_hsl(o2[0], o2[1], o2[2])
    print(f"\n  {name}:")
    print(f"    v1: H={float(h1):.1f}° S={float(s1):.3f} L={float(l1):.3f}")
    print(f"    v2: H={float(h2):.1f}° S={float(s2):.3f} L={float(l2):.3f}")
    print(f"    Δ:  H={float(h2-h1):+.1f}° S={float(s2-s1):+.3f} L={float(l2-l1):+.3f}")

# ── 整体变化幅度 ──
print(f"\n{'='*60}")
print("整体变化量评估")
print("=" * 60)
# 评估 v1 和 v2 各自偏离"中性"的程度
neutral_params = {
    'tone': {'black_lift': 0, 'shadow_toe_pivot': 0, 'shadow_toe_power': 1,
             'contrast': 1, 'per_channel_contrast': [1,1,1],
             'highlight_shoulder_start': 1, 'highlight_shoulder_power': 1},
    'color': {'shadow_tint': [1,1,1], 'highlight_tint': [1,1,1],
              'global_saturation': 1, 'highlight_desat_start': 1, 'highlight_desat_max': 0,
              'skin_hue_min': 0, 'skin_hue_max': 360, 'skin_sat_adjust': 1,
              'teal_push': 0, 'orange_push': 0,
              'blue_saturation_boost': 1, 'blue_luminance_shift': 0, 'blue_hue_shift': 0,
              'white_balance_shift_k': 0},
}

def avg_deviation(params):
    """量化偏离中性的程度（对各测试色的平均 RGB 变化）"""
    total = 0
    count = 0
    for h in [0, 30, 60, 120, 180, 210, 240, 300]:
        for s in [0.3, 0.5, 0.7]:
            for l in [0.3, 0.5, 0.7]:
                r, g, b = hsl_to_rgb(np.array([float(h)]), np.array([float(s)]), np.array([float(l)]))
                rgb = np.array([float(r.item()), float(g.item()), float(b.item())])
                neutral = pipeline(rgb, neutral_params)
                styled = pipeline(rgb, params)
                total += np.mean(np.abs(styled - neutral))
                count += 1
    return total / count

d1 = avg_deviation(v1)
d2 = avg_deviation(v2)
print(f"  v1 平均偏离中性: {d1:.5f}")
print(f"  v2 平均偏离中性: {d2:.5f}")
print(f"  v2 是 v1 的:    {d2/d1*100:.0f}%")
