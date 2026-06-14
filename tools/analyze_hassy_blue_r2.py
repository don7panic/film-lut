#!/usr/bin/env python3
"""
Hasselblad HNCS 色彩审计 — Round 2: 交互效应 & 结构性分析
===========================================================
1. Isolate WB contribution to blue saturation
2. Analyze tone curve shape vs "Hasselblad Film Curve" description
3. Check pipeline artifacts (HSL round-trip, hue discontinuities)
4. V-Log path analysis
"""

import sys
import os
import numpy as np

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


def main():
    params = load_preset('hassy_blue')
    t = params['tone']
    c = params['color']

    # Full pipeline
    def full_pipeline(rgb_linear):
        tonemapped = apply_tone_curve(rgb_linear, params)
        graded = apply_color_grade(tonemapped, params)
        return linear_to_display(graded)

    def tone_only(rgb_linear):
        tonemapped = apply_tone_curve(rgb_linear, params)
        return linear_to_display(tonemapped)

    def tone_only_linear(rgb_linear):
        return apply_tone_curve(rgb_linear, params)

    # ═══════════════════════════════════════════════════════════════════
    # R2A: Isolate WB contribution to blue saturation
    # ═══════════════════════════════════════════════════════════════════
    print("=" * 72)
    print("  R2A: WB Shift Contribution to Blue Saturation")
    print("=" * 72)

    # Build a version WITHOUT WB shift
    params_no_wb = load_preset('hassy_blue')
    params_no_wb = params_no_wb.copy()
    params_no_wb['color'] = params_no_wb['color'].copy()
    params_no_wb['color']['white_balance_shift_k'] = 0.0

    def pipeline_no_wb(rgb_linear):
        tonemapped = apply_tone_curve(rgb_linear, params_no_wb)
        graded = apply_color_grade(tonemapped, params_no_wb)
        return linear_to_display(graded)

    def pipeline_no_blueboost(rgb_linear):
        tonemapped = apply_tone_curve(rgb_linear, params)
        c2 = params['color'].copy()
        c2['blue_saturation_boost'] = 1.0
        c2['blue_luminance_shift'] = 0.0
        c2['blue_hue_shift'] = 0.0
        params2 = params.copy()
        params2['color'] = c2
        graded = apply_color_grade(tonemapped, params2)
        return linear_to_display(graded)

    print(f"\n  Blue (240°, sat=0.7, lum=0.5) saturation breakdown:")
    r, g, b = hsl_to_rgb(np.array([240.0]), np.array([0.7]), np.array([0.5]))
    rgb_in = np.array([float(r.item()), float(g.item()), float(b.item())])
    
    out_full = full_pipeline(rgb_in)
    out_no_wb = pipeline_no_wb(rgb_in)
    out_no_bb = pipeline_no_blueboost(rgb_in)
    
    _, s_full, _ = rgb_to_hsl(out_full[0], out_full[1], out_full[2])
    _, s_no_wb, _ = rgb_to_hsl(out_no_wb[0], out_no_wb[1], out_no_wb[2])
    _, s_no_bb, _ = rgb_to_hsl(out_no_bb[0], out_no_bb[1], out_no_bb[2])
    
    print(f"    Full pipeline:     sat={float(s_full):.3f}")
    print(f"    No WB shift:       sat={float(s_no_wb):.3f}  (Δ from full: {float(s_no_wb - s_full):+.3f})")
    print(f"    No blue boost:     sat={float(s_no_bb):.3f}  (Δ from full: {float(s_no_bb - s_full):+.3f})")
    print(f"    → WB contributes {float(s_full - s_no_wb):+.3f} sat boost (B channel amplification)")
    print(f"    → Blue boost contributes {float(s_full - s_no_bb):+.3f} sat boost (explicit param)")

    # ═══════════════════════════════════════════════════════════════════
    # R2B: Tone Curve Shape Analysis
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("  R2B: Tone Curve Shape vs 'Hasselblad Film Curve'")
    print("=" * 72)

    print(f"\n  'Hasselblad Film Curve' expected characteristics:")
    print(f"    • Perceptually-aware (not technical gamma)")
    print(f"    • Enhanced midtone contrast")
    print(f"    • Smooth shadow and highlight roll-off")
    print(f"    • Film-like tonal transitions")

    # Generate a fine-grained tone curve
    x = np.linspace(0, 1, 101)
    y = tone_only(np.column_stack([x, x, x]))
    y_avg = y.mean(axis=1)

    print(f"\n  Actual Tone Curve Characteristics (tone-only, neutral gray):")
    print(f"    Contrast power:  {t['contrast']:.2f} (< 1 = lift mids, lower contrast)")
    print(f"    Shadow toe:      pivot={t['shadow_toe_pivot']:.2f}, power={t['shadow_toe_power']:.2f}")
    print(f"    Highlight shldr: start={t['highlight_shoulder_start']:.2f}, power={t['highlight_shoulder_power']:.2f}")

    # Find the contrast inflection point (where output crosses input)
    for i in range(len(x)):
        if y_avg[i] >= x[i]:
            cross_idx = i
            break
    
    cross_point = x[cross_idx]
    print(f"\n    Curve crosses input line at: x ≈ {cross_point:.3f}")
    print(f"    Below {cross_point:.3f}: output > input (shadow lifted)")
    print(f"    Above {cross_point:.3f}: output < input (mids compressed)")

    # Check effective gamma at mid-gray
    mid_idx = 50  # x=0.50
    eff_gamma = np.log(y_avg[mid_idx]) / np.log(x[mid_idx]) if x[mid_idx] > 0 else 0
    print(f"\n    Effective gamma at mid-gray (0.50): {eff_gamma:.4f}")
    print(f"    Output at 0.50: {y_avg[50]:.4f}")

    # Contrast analysis: Δoutput / Δinput in midtone region
    for region, start_i, end_i in [("Deep shadow", 1, 8), ("Shadow", 12, 23), ("Mid-low", 25, 40), ("Mid", 40, 60), ("Mid-high", 60, 75), ("Highlight", 85, 98)]:
        dx = x[end_i] - x[start_i]
        dy = y_avg[end_i] - y_avg[start_i]
        slope = dy / dx if dx > 0 else 0
        print(f"    {region:>14} ({x[start_i]:.2f}-{x[end_i]:.2f}): slope={slope:.3f}")

    # HNCS description says "enhanced midtone contrast"
    # But our contrast=0.95 (<1) means we REDUCE midtone contrast!
    print(f"\n  ⚠  Analysis: contrast={t['contrast']:.2f} < 1.0 means midtone contrast is REDUCED,")
    print(f"     which contradicts HNCS 'enhanced midtone contrast' description.")

    # ═══════════════════════════════════════════════════════════════════
    # R2C: Hue Continuity Check (200-270° range)
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("  R2C: Blue Hue Continuity (fine sampling of 180-280°)")
    print("=" * 72)

    fine_hues = np.linspace(180, 280, 41)
    print(f"\n  {'H_in':>6}  {'H_out':>7}  {'ΔH':>7}  {'Direction':>10}")
    print(f"  {'─'*6}  {'─'*7}  {'─'*7}  {'─'*10}")
    
    dh_list = []
    for h in fine_hues:
        r, g, b = hsl_to_rgb(np.array([h]), np.array([0.7]), np.array([0.5]))
        rgb_in = np.array([float(r.item()), float(g.item()), float(b.item())])
        out = full_pipeline(rgb_in)
        ho, _, _ = rgb_to_hsl(out[0], out[1], out[2])
        dh = float(ho - h)
        dh_list.append({'h_in': h, 'h_out': float(ho), 'dh': dh})
        
        direction = "→green" if dh < -1 else ("→purple" if dh > 1 else "≈neutral")
        print(f"  {h:6.1f}  {float(ho):7.1f}  {dh:+7.1f}  {direction:>10}")

    # Find discontinuity
    max_jump = 0
    jump_h = 0
    for i in range(1, len(dh_list)):
        jump = abs(dh_list[i]['dh'] - dh_list[i-1]['dh'])
        if jump > max_jump:
            max_jump = jump
            jump_h = dh_list[i]['h_in']
    
    print(f"\n  Max hue shift discontinuity: {max_jump:.1f}° at h≈{jump_h:.0f}°")

    # ═══════════════════════════════════════════════════════════════════
    # R2D: HSL Round-trip Artifact Check
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("  R2D: HSL Round-trip Artifact Check (sat=0.7, lum=0.5)")
    print("=" * 72)
    
    print(f"\n  {'H_in':>6}  {'H_rt':>7}  {'ΔH_rt':>7}  {'S_in':>6}  {'S_rt':>6}  {'ΔS_rt':>7}")
    print(f"  {'─'*6}  {'─'*7}  {'─'*7}  {'─'*6}  {'─'*6}  {'─'*7}")
    for h in [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]:
        r, g, b = hsl_to_rgb(np.array([float(h)]), np.array([0.7]), np.array([0.5]))
        hi, si, _ = rgb_to_hsl(float(r.item()), float(g.item()), float(b.item()))
        dh = float(hi - h)
        ds = float(si - 0.7)
        print(f"  {h:6.0f}  {float(hi):7.1f}  {dh:+7.1f}  {0.7:6.1f}  {float(si):6.3f}  {ds:+7.3f}")

    # ═══════════════════════════════════════════════════════════════════
    # R2E: V-Log LUT Path Analysis
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("  R2E: V-Log Path Analysis — V-Gamut → Rec.709 Matrix")
    print("=" * 72)

    from engine.core import M_VGAMUT_TO_REC709
    print(f"\n  V-Gamut → Rec.709 Matrix:")
    for row in M_VGAMUT_TO_REC709:
        print(f"    [{row[0]:+.6f}  {row[1]:+.6f}  {row[2]:+.6f}]")

    # Test: V-Log pure blue → what happens in gamut conversion
    # V-Log 0.5 ≈ 18% gray (typical exposure)
    # For pure saturated blue in V-Gamut:
    vlog_blue = np.array([0.3, 0.3, 0.7])  # V-Log encoding
    lin_vgamut = vlog_to_linear(vlog_blue)
    lin_rec709 = vgamut_to_rec709(lin_vgamut)
    
    # Apply pipeline
    tonemapped = apply_tone_curve(lin_rec709, params)
    graded = apply_color_grade(tonemapped, params)
    display = linear_to_display(graded)
    
    print(f"\n  V-Log Blue Path (V-Log B=0.7, G=0.3, R=0.3):")
    print(f"    V-Log input:        R={vlog_blue[0]:.3f} G={vlog_blue[1]:.3f} B={vlog_blue[2]:.3f}")
    print(f"    Linear V-Gamut:     R={lin_vgamut[0]:.4f} G={lin_vgamut[1]:.4f} B={lin_vgamut[2]:.4f}")
    print(f"    Linear Rec.709:     R={lin_rec709[0]:.4f} G={lin_rec709[1]:.4f} B={lin_rec709[2]:.4f}")
    ho, so, lo = rgb_to_hsl(display[0], display[1], display[2])
    print(f"    Display output HSL: H={float(ho):.1f}° S={float(so):.3f} L={float(lo):.3f}")
    
    # V-Log neutral gray
    vlog_gray = np.array([0.5, 0.5, 0.5])
    lin_vg_gray = vlog_to_linear(vlog_gray)
    lin_709_gray = vgamut_to_rec709(lin_vg_gray)
    print(f"\n  V-Log Gray Path (V-Log 0.5, 0.5, 0.5 = ~18% gray):")
    print(f"    Linear V-Gamut:     R={lin_vg_gray[0]:.4f} G={lin_vg_gray[1]:.4f} B={lin_vg_gray[2]:.4f}")
    print(f"    Linear Rec.709:     R={lin_709_gray[0]:.4f} G={lin_709_gray[1]:.4f} B={lin_709_gray[2]:.4f}")
    
    # Apply full V-Log pipeline
    toned = apply_tone_curve(lin_709_gray, params)
    graded = apply_color_grade(toned, params)
    disp = linear_to_display(graded)
    print(f"    Display output:     R={disp[0]:.4f} G={disp[1]:.4f} B={disp[2]:.4f}")

    # ═══════════════════════════════════════════════════════════════════
    # R2F: Saturation behavior — is "natural but better than accurate" achieved?
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("  R2F: 'Natural but Better Than Accurate' Assessment")
    print("=" * 72)

    # HNCS: global_sat ≈ slightly desaturated for natural look, but perceptually enhanced
    print(f"\n  Global saturation multiplier: {c['global_saturation']:.2f}")
    print(f"  Blue-specific boost:          {c['blue_saturation_boost']:.2f}")
    print(f"  Net blue effective (h=240°):  {c['global_saturation'] * c['blue_saturation_boost']:.3f}")
    
    # Check if overall saturation is truly "natural"
    avg_color_sat_change = 0
    for h in [0, 30, 60, 120, 180, 240, 300]:
        r, g, b = hsl_to_rgb(np.array([float(h)]), np.array([0.7]), np.array([0.5]))
        rgb_in = np.array([float(r.item()), float(g.item()), float(b.item())])
        out = full_pipeline(rgb_in)
        _, so, _ = rgb_to_hsl(out[0], out[1], out[2])
        avg_color_sat_change += float(so - 0.7)
    avg_color_sat_change /= 7
    print(f"\n  Average saturation change (across 7 hues at sat=0.7): {avg_color_sat_change:+.3f}")
    print(f"  → {'Natural desaturation' if avg_color_sat_change < 0 else 'Net saturation increase'}")

    # ═══════════════════════════════════════════════════════════════════
    # R2G: Structural Limitations
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("  R2G: Pipeline Structural Limitations vs HNCS")
    print("=" * 72)
    
    limitations = [
        ("Per-pixel calibration", 
         "HNCS calibrates every pixel on sensor. We use a uniform 33³ 3D LUT.",
         "Cannot replicate — fundamental hardware difference"),
        ("L*RGB color space",
         "HNCS uses perceptually uniform LAB-derived space. We use Rec.709 linear + HSL.",
         "HSL is NOT perceptually uniform — equal ΔH steps don't correspond to equal perceived differences"),
        ("Scene-referred pipeline",
         "HNCS operates on sensor data with known spectral sensitivity. Our V-Log path approximates.",
         "V-Log is a reasonable approximation of scene-linear, but not spectrally matched"),
        ("3D LUT interpolation",
         "33³ trilinear interpolation. 10° hue shifts straddle multiple grid cells.",
         "Precision adequate for display, but boundaries may have artifacts"),
        ("No inter-layer cross effects",
         "Real color negative has layer-to-layer spectral crosstalk. We process RGB independently.",
         "Not applicable — HNCS is for digital, but our 5219 LUT similarly lacks this"),
    ]
    
    for i, (name, issue, impact) in enumerate(limitations, 1):
        print(f"\n  {i}. {name}")
        print(f"     Issue:  {issue}")
        print(f"     Impact: {impact}")


if __name__ == '__main__':
    main()
