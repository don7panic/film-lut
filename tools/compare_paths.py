#!/usr/bin/env python3
"""对比 Standard vs V-Log 路径效果"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.core import (apply_tone_curve, apply_color_grade, linear_to_display,
                          vlog_to_linear, vgamut_to_rec709, DISPLAY_GAMMA)
from engine.preset import load_preset

params = load_preset('hassy_blue')

print("=" * 65)
print("Standard vs V-Log 路径对比")
print("=" * 65)

# Standard path
def standard_path(rgb_in):
    """Rec.709 display → inverse gamma → linear → pipeline → display gamma"""
    thresh = 0.04045
    linear = np.where(rgb_in <= thresh, rgb_in / 12.92,
                      ((rgb_in + 0.055) / 1.055) ** DISPLAY_GAMMA)
    toned = apply_tone_curve(linear, params)
    graded = apply_color_grade(toned, params)
    return linear_to_display(graded)

# V-Log path
def vlog_path(rgb_in):
    """V-Log → linear → gamut → pipeline → display gamma"""
    linear_v = vlog_to_linear(rgb_in)
    linear_709 = vgamut_to_rec709(linear_v)
    toned = apply_tone_curve(linear_709, params)
    graded = apply_color_grade(toned, params)
    return linear_to_display(graded)

# Test: neutral gray ramp
print(f"\n{'Input':>8} {'Std_avg':>9} {'Std_B-R':>8} {'VLog_avg':>9} {'VLog_B-R':>8} {'VLog_valid':>10}")
print(f"{'─'*8} {'─'*9} {'─'*8} {'─'*9} {'─'*8} {'─'*10}")

for lvl in np.linspace(0.05, 0.95, 10):
    g = np.array([lvl]*3)
    so = standard_path(g)
    vo = vlog_path(g)
    v_ok = "✓" if np.all(vo > 0.001) else "⚠ DEAD"
    print(f"{lvl:8.2f} {np.mean(so):9.4f} {so[2]-so[0]:+8.4f} {np.mean(vo):9.4f} {vo[2]-vo[0]:+8.4f} {v_ok:>10}")

# Test: some colors
print(f"\n色彩测试:")
for name, rgb in [("Blue", [0.2,0.2,0.8]), ("Skin", [0.7,0.5,0.35]), ("Green", [0.15,0.6,0.15])]:
    so = standard_path(np.array(rgb))
    vo = vlog_path(np.array(rgb))
    v_ok = "✓" if np.all(vo > 0.001) else "⚠ DEAD"
    print(f"  {name}: Std=({so[0]:.3f},{so[1]:.3f},{so[2]:.3f})  VLog=({vo[0]:.3f},{vo[1]:.3f},{vo[2]:.3f})  {v_ok}")

# Check V-Log shadow deadzone
print(f"\nV-Log 阴影死区检查:")
for v in [0.05, 0.10, 0.125, 0.15, 0.18, 0.20]:
    lin = vlog_to_linear(np.array([v, v, v]))
    print(f"  V-Log {v:.3f} → linear [{lin[0]:.6f}, {lin[1]:.6f}, {lin[2]:.6f}] {'⚠ DEAD' if np.all(lin < 0.00001) else ''}")
