#!/usr/bin/env python3
"""
Hasselblad HNCS 色彩差异审计 — Test Vector Pass
==================================================
对 hassy_blue LUT 管线进行端到端分析，量化各维度色彩偏移。

用法: uv run python tools/analyze_hassy_blue.py
"""

import sys
import os
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import (
    apply_tone_curve,
    apply_color_grade,
    linear_to_display,
    rgb_to_hsl,
    hsl_to_rgb,
    vlog_to_linear,
    vgamut_to_rec709,
)
from engine.preset import load_preset


def analyze_preset(preset_name='hassy_blue'):
    """Run comprehensive test vector pass and print results."""
    params = load_preset(preset_name)
    t = params['tone']
    c = params['color']

    print("=" * 72)
    print(f"  Hasselblad HNCS Color Audit — {preset_name}")
    print("=" * 72)
    print(f"\n  Tone Parameters:")
    print(f"    Black lift:             {t['black_lift']:.5f}")
    print(f"    Shadow toe:             pivot={t['shadow_toe_pivot']:.2f}, power={t['shadow_toe_power']:.2f}")
    ch = t['per_channel_contrast']
    print(f"    Contrast:               base={t['contrast']:.2f}, per-channel R={t['contrast']*ch[0]:.3f} G={t['contrast']*ch[1]:.3f} B={t['contrast']*ch[2]:.3f}")
    print(f"    Highlight shoulder:     start={t['highlight_shoulder_start']:.2f}, power={t['highlight_shoulder_power']:.2f}")
    print(f"\n  Color Parameters:")
    print(f"    Global saturation:      {c['global_saturation']:.2f}")
    print(f"    Highlight desat:        start={c['highlight_desat_start']:.2f}, max={c['highlight_desat_max']:.2f}")
    print(f"    Skin tone:              hue={c['skin_hue_min']:.0f}-{c['skin_hue_max']:.0f}°, sat_adj={c['skin_sat_adjust']:.2f}")
    print(f"    Shadow tint:            R={c['shadow_tint'][0]:.2f} G={c['shadow_tint'][1]:.2f} B={c['shadow_tint'][2]:.2f}")
    print(f"    Highlight tint:         R={c['highlight_tint'][0]:.2f} G={c['highlight_tint'][1]:.2f} B={c['highlight_tint'][2]:.2f}")
    print(f"    Teal/Orange push:       teal={c['teal_push']:+.0f}°, orange={c['orange_push']:+.0f}°")
    print(f"    Blue boost:             sat={c['blue_saturation_boost']:.2f}, lum={c['blue_luminance_shift']:+.2f}, hue={c['blue_hue_shift']:+.1f}°")
    print(f"    White balance:          {c['white_balance_shift_k']:+.0f}K")

    # Full pipeline function
    def full_pipeline(rgb_linear):
        tonemapped = apply_tone_curve(rgb_linear, params)
        graded = apply_color_grade(tonemapped, params)
        return linear_to_display(graded)

    def tone_only(rgb_linear):
        tonemapped = apply_tone_curve(rgb_linear, params)
        return linear_to_display(tonemapped)

    # ═══════════════════════════════════════════════════════════════════
    # D1: Neutral Grayscale Tone Curve Analysis
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 72)
    print("  D1: Neutral Grayscale — Tone Curve Analysis")
    print("─" * 72)

    gray_levels = [0.01, 0.02, 0.05, 0.10, 0.18, 0.25, 0.35, 0.50, 0.65, 0.75, 0.85, 0.95, 1.00]
    
    print(f"\n  {'Input':>8}  {'R_tone':>8}  {'G_tone':>8}  {'B_tone':>8}  {'RGB_avg':>8}  {'Bias':>8}  {'R_full':>8}  {'G_full':>8}  {'B_full':>8}  {'Full_avg':>8}  {'Bias':>8}  {'Contrast':>10}")
    print(f"  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*10}")

    for lvl in gray_levels:
        gray = np.array([lvl, lvl, lvl])
        
        # Tone curve only
        tone_rgb = tone_only(gray)
        tone_avg = np.mean(tone_rgb)
        tone_bias = tone_rgb[2] - tone_rgb[0]  # B - R: positive = cool, negative = warm
        
        # Full pipeline
        full_rgb = full_pipeline(gray)
        full_avg = np.mean(full_rgb)
        full_bias = full_rgb[2] - full_rgb[0]
        
        # Perceived contrast: Δluma / Δinput
        print(f"  {lvl:8.3f}  {tone_rgb[0]:8.4f}  {tone_rgb[1]:8.4f}  {tone_rgb[2]:8.4f}  {tone_avg:8.4f}  {tone_bias:+8.4f}  {full_rgb[0]:8.4f}  {full_rgb[1]:8.4f}  {full_rgb[2]:8.4f}  {full_avg:8.4f}  {full_bias:+8.4f}")

    # ═══════════════════════════════════════════════════════════════════
    # D1b: per_channel_contrast gray rendering check
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n  Per-Channel Contrast Effect (neutral gray only, tone curve):")
    pc = np.asarray(t['per_channel_contrast'], dtype=np.float64)
    eff_r = t['contrast'] * pc[0]
    eff_g = t['contrast'] * pc[1]
    eff_b = t['contrast'] * pc[2]
    print(f"    R: {eff_r:.3f}  G: {eff_g:.3f}  B: {eff_b:.3f}")
    if eff_b > eff_r:
        print(f"    → B channel has HIGHEST contrast → neutral gray shifts COOL (B brightest)")
    elif eff_b < eff_r:
        print(f"    → B channel has LOWEST contrast → neutral gray shifts WARM (R brightest)")
    else:
        print(f"    → All channels equal → neutral gray stays NEUTRAL")

    # ═══════════════════════════════════════════════════════════════════
    # D2: Blue Rendering Analysis
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 72)
    print("  D2: Blue Rendering — Hue/Saturation/Luminance Shift in 200-260°")
    print("─" * 72)

    blue_test_hues = [180, 195, 200, 210, 225, 240, 255, 260, 270]
    sat_levels = [0.3, 0.5, 0.7, 1.0]
    lum_levels = [0.3, 0.5, 0.7]

    print(f"\n  Blue Hue Shift Analysis (sat=0.7, lum=0.5):")
    print(f"  {'Input':>8}  {'Before H':>9}  {'After H':>9}  {'ΔHue':>7}  {'Before S':>9}  {'After S':>9}  {'ΔSat':>7}  {'Before L':>9}  {'After L':>9}  {'ΔLum':>7}")
    print(f"  {'─'*8}  {'─'*9}  {'─'*9}  {'─'*7}  {'─'*9}  {'─'*9}  {'─'*7}  {'─'*9}  {'─'*9}  {'─'*7}")

    for h in blue_test_hues:
        r, g, b = hsl_to_rgb(np.array([h]), np.array([0.7]), np.array([0.5]))
        rgb_in = np.array([float(r.item()), float(g.item()), float(b.item())])
        
        # Input HSL
        hi, si, li = rgb_to_hsl(rgb_in[0], rgb_in[1], rgb_in[2])
        
        # Full pipeline
        out = full_pipeline(rgb_in)
        ho, so, lo = rgb_to_hsl(out[0], out[1], out[2])
        
        dh = float(ho - hi)
        ds = float(so - si)
        dl = float(lo - li)
        
        print(f"  {h:8.0f}°  {float(hi):9.1f}°  {float(ho):9.1f}°  {dh:+7.1f}°  {float(si):9.3f}  {float(so):9.3f}  {ds:+7.3f}  {float(li):9.3f}  {float(lo):9.3f}  {dl:+7.3f}")

    # Check blue saturation boost effect across sat levels
    print(f"\n  Blue Saturation Boost by Input Saturation (hue=240°, lum=0.5):")
    print(f"  {'S_in':>8}  {'S_out':>8}  {'ΔSat':>7}  {'Multiplier':>10}")
    print(f"  {'─'*8}  {'─'*8}  {'─'*7}  {'─'*10}")
    for s in [0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]:
        r, g, b = hsl_to_rgb(np.array([240.0]), np.array([s]), np.array([0.5]))
        rgb_in = np.array([float(r.item()), float(g.item()), float(b.item())])
        out = full_pipeline(rgb_in)
        _, so, _ = rgb_to_hsl(out[0], out[1], out[2])
        mult = float(so / s) if s > 0 else 0
        print(f"  {s:8.2f}  {float(so):8.3f}  {float(so-s):+7.3f}  {mult:10.3f}")

    # ═══════════════════════════════════════════════════════════════════
    # D3: Skin Tone Analysis
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 72)
    print("  D3: Skin Tone Reproduction")
    print("─" * 72)
    
    skin_test_hues = [10, 15, 20, 25, 30, 35, 40, 42, 45]
    print(f"\n  Skin Tone Saturation Adjustment (sat=0.5, lum=0.5):")
    print(f"  {'Hue':>6}  {'Within?':>8}  {'S_in':>6}  {'S_out':>6}  {'ΔSat':>7}")
    print(f"  {'─'*6}  {'─'*8}  {'─'*6}  {'─'*6}  {'─'*7}")
    
    skin_min = c['skin_hue_min']
    skin_max = c['skin_hue_max']
    
    for h in skin_test_hues:
        r, g, b = hsl_to_rgb(np.array([float(h)]), np.array([0.5]), np.array([0.5]))
        rgb_in = np.array([float(r.item()), float(g.item()), float(b.item())])
        out = full_pipeline(rgb_in)
        _, so, _ = rgb_to_hsl(out[0], out[1], out[2])
        
        hi, si, li = rgb_to_hsl(rgb_in[0], rgb_in[1], rgb_in[2])
        within = "✓" if (skin_min <= h <= skin_max and float(si) > 0.05 and float(li) > 0.15 and float(li) < 0.85) else "—"
        
        print(f"  {h:6.0f}°  {within:>8}  {float(si):6.3f}  {float(so):6.3f}  {float(so-si):+7.3f}")

    # Check skin tone protection range vs known skin tone science
    print(f"\n  Skin Protection Range Analysis:")
    print(f"    Current range: {skin_min:.0f}° – {skin_max:.0f}°")
    print(f"    Typical Caucasian:   15° – 35°")
    print(f"    Typical Asian:       20° – 40°")
    print(f"    Typical African:     15° – 35°")
    
    if skin_max > 40:
        print(f"    ⚠ skin_hue_max={skin_max:.0f}° extends into pure orange zone (>40°)")

    # ═══════════════════════════════════════════════════════════════════
    # D4: Overall Saturation
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 72)
    print("  D4: Overall Saturation Behavior")
    print("─" * 72)

    color_test = [
        ("Red",       0,   0.7, 0.5),
        ("Orange",   30,   0.7, 0.5),
        ("Yellow",   60,   0.7, 0.5),
        ("Green",   120,   0.7, 0.5),
        ("Teal",    180,   0.7, 0.5),
        ("Blue",    240,   0.7, 0.5),
        ("Purple",  280,   0.7, 0.5),
        ("Magenta", 320,   0.7, 0.5),
    ]

    baseline_s = 0.7
    baseline_l = 0.5
    print(f"\n  Color Check at sat={baseline_s}, lum={baseline_l}:")
    print(f"  {'Color':>8}  {'H_in':>6}  {'H_out':>6}  {'ΔH':>6}  {'S_in':>6}  {'S_out':>6}  {'ΔS':>7}  {'L_in':>6}  {'L_out':>6}  {'ΔL':>7}")
    print(f"  {'─'*8}  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*7}  {'─'*6}  {'─'*6}  {'─'*7}")
    
    for name, h, s, l in color_test:
        r, g, b = hsl_to_rgb(np.array([float(h)]), np.array([float(s)]), np.array([float(l)]))
        rgb_in = np.array([float(r.item()), float(g.item()), float(b.item())])
        hi, si, li = rgb_to_hsl(rgb_in[0], rgb_in[1], rgb_in[2])
        
        out = full_pipeline(rgb_in)
        ho, so, lo = rgb_to_hsl(out[0], out[1], out[2])
        
        dh = float(ho - hi)
        ds = float(so - si)
        dl = float(lo - li)
        
        print(f"  {name:>8}  {float(hi):6.1f}  {float(ho):6.1f}  {dh:+6.1f}  {float(si):6.3f}  {float(so):6.3f}  {ds:+7.3f}  {float(li):6.3f}  {float(lo):6.3f}  {dl:+7.3f}")

    # ═══════════════════════════════════════════════════════════════════
    # D5: White Balance Effect
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 72)
    print("  D5: White Balance Shift Effect")
    print("─" * 72)
    
    wb_k = c.get('white_balance_shift_k', 0)
    factor = wb_k / 10000.0
    print(f"\n    WB shift: {wb_k:+.0f}K → R factor={1+factor:.3f}, B factor={1-factor:.3f}")
    
    # Effect on neutral gray
    for lvl in [0.18, 0.50]:
        gray = np.array([lvl, lvl, lvl])
        out = full_pipeline(gray)
        print(f"    Gray {lvl:.2f}: output R={out[0]:.4f} G={out[1]:.4f} B={out[2]:.4f} → B-R={out[2]-out[0]:+.4f}")

    # ═══════════════════════════════════════════════════════════════════
    # D6: Shadow/Highlight Transition
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 72)
    print("  D6: Shadow / Highlight Transition")
    print("─" * 72)
    
    # Shadow tint effect
    shadow_t = c['shadow_tint']
    highlight_t = c['highlight_tint']
    print(f"\n    Shadow tint:     R={shadow_t[0]:.3f} G={shadow_t[1]:.3f} B={shadow_t[2]:.3f}")
    print(f"    Highlight tint:  R={highlight_t[0]:.3f} G={highlight_t[1]:.3f} B={highlight_t[2]:.3f}")
    
    # Check shadow behavior
    print(f"\n    Shadow Tint Effect on Dark Neutral Gray (input=0.05):")
    gray = np.array([0.05, 0.05, 0.05])
    out = full_pipeline(gray)
    print(f"    Output: R={out[0]:.4f} G={out[1]:.4f} B={out[2]:.4f} → {'Cool shadow' if out[2] > out[0] else 'Warm shadow' if out[2] < out[0] else 'Neutral shadow'}")

    # Check highlight behavior
    print(f"\n    Highlight Tint Effect on Light Gray (input=0.85):")
    gray = np.array([0.85, 0.85, 0.85])
    out = full_pipeline(gray)
    print(f"    Output: R={out[0]:.4f} G={out[1]:.4f} B={out[2]:.4f} → {'Cool highlight' if out[2] > out[0] else 'Warm highlight' if out[2] < out[0] else 'Neutral highlight'}")

    # Toe / shoulder visual check points
    print(f"\n    Tone Curve Check Points (Tone Only):")
    for name, lvl in [("Deep shadow", 0.02), ("Shadow", 0.10), ("Mid-low", 0.25), ("Mid", 0.50), ("Mid-high", 0.70), ("Highlight", 0.90)]:
        gray = np.array([lvl, lvl, lvl])
        out = tone_only(gray)
        print(f"      {name:>12} ({lvl:.2f}): R={out[0]:.4f} G={out[1]:.4f} B={out[2]:.4f} avg={np.mean(out):.4f}")
    
    # ───────────────────────────────────────────────────────────────
    # D6b: Black Lift
    # ───────────────────────────────────────────────────────────────
    black_lift = t['black_lift']
    print(f"\n    Black Lift: {black_lift:.5f}")
    print(f"    → All values below {black_lift:.5f} are raised to {black_lift:.5f}")
    print(f"    → In 8-bit: floor = {int(black_lift*255)} (film base fog simulation)")

    # ───────────────────────────────────────────────────────────────
    # D8 Check: Tone curve headroom
    # ───────────────────────────────────────────────────────────────
    print(f"\n    Highlight Shoulder: start={t['highlight_shoulder_start']:.2f}, power={t['highlight_shoulder_power']:.2f}")
    hss = t['highlight_shoulder_start']
    hsp = t['highlight_shoulder_power']
    for lvl in [hss - 0.05, hss, hss + 0.05, 0.85, 0.95, 1.0]:
        gray = np.array([lvl, lvl, lvl])
        out = tone_only(gray)
        print(f"      Input={lvl:.3f}: avg_out={np.mean(out):.4f} ({'compressed' if lvl > hss else 'linear zone'})")

    # ═══════════════════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("  Summary Highlights")
    print("=" * 72)
    
    # D1: Tone curve neutral bias
    mid_gray = np.array([0.50, 0.50, 0.50])
    tone_mid = tone_only(mid_gray)
    mid_bias = tone_mid[2] - tone_mid[0]
    print(f"\n  D1 Tone Curve: Mid-gray R-B bias = {mid_bias:+.5f}")

    # D2: Blue hue shift at 240°
    r, g, b = hsl_to_rgb(np.array([240.0]), np.array([0.7]), np.array([0.5]))
    rgb_in = np.array([float(r.item()), float(g.item()), float(b.item())])
    out = full_pipeline(rgb_in)
    ho, so, lo = rgb_to_hsl(out[0], out[1], out[2])
    print(f"  D2 Blue (240°, sat=0.7): ΔH={float(ho-240):+.1f}°, ΔS={float(so-0.7):+.3f}, ΔL={float(lo-0.5):+.3f}")

    # Overall neutral color temperature
    print(f"\n  Overall WB: {c['white_balance_shift_k']:+.0f}K → {'Cool' if c['white_balance_shift_k'] < 0 else 'Warm'} bias")
    print(f"  Skin range: {c['skin_hue_min']:.0f}° – {c['skin_hue_max']:.0f}°")
    print(f"  Global sat: {c['global_saturation']:.2f}")
    
    print("\n" + "=" * 72)


if __name__ == '__main__':
    analyze_preset('hassy_blue')
