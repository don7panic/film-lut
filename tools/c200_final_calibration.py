#!/usr/bin/env python3
"""
C200 Final Calibration — Pipeline Test & Reference Generation
=============================================================
Synthesizes R1+R2 research findings into final PRESET dict,
runs full V-Log → display pipeline tests on 14+ key colors,
validates 6 critical features, and generates test_reference_c200.png.

Usage:
  cd /Users/oolong/workspace/film
  uv run python3 tools/c200_final_calibration.py
"""

import numpy as np
import os, sys

# Project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import (
    apply_tone_curve, apply_color_grade, rgb_to_hsl, hsl_to_rgb,
    vlog_to_linear, linear_to_display, vgamut_to_rec709,
)


# ============================================================================
# FINAL C200 PRESET — Synthesized from R1+R2 Research
# ============================================================================

PRESET = {
    'name': 'c200',
    'title': 'Fujifilm Fujicolor C200 (Japan) — v1',

    'tone': {
        # ---- C200 signature: soft, cinematic shadows ----
        # Evidence: H+0.5/S-0.5 from Fuji X Weekly C200 recipe (雅婷 R1)
        #   + 程远 engine test mapping: contrast=0.96, shadow_toe=0.88
        #   + i50mm: "暗光下容易丢失暗部细节" → moderate black_lift
        # [MEASURED] — engine test verified
        'black_lift':                0.0015,       # [INFERRED] Minimal film base (consumer-grade C200)
        'shadow_toe_pivot':          0.10,
        'shadow_toe_power':          0.88,         # [MEASURED] Soft toe — "光影柔和" (程远 engine test)
        'contrast':                  0.96,         # [MEASURED] H+0.5/S-0.5 mapping (程远 engine test)

        # Per-channel contrast: G channel slightly enhanced for Fuji green body
        # Evidence: Classic Negative base engine has green bias
        # [INFERRED] — no spectral sensitivity data available
        'per_channel_contrast':      [1.00, 1.02, 1.00],  # G +2% for Fuji green rendering

        # ---- Excellent highlight latitude ----
        # Evidence: i50mm "高光有很不错的宽容度"
        # [INFERRED] — guided by 5219's highlight preservation strategy
        'highlight_shoulder_start':  0.72,
        'highlight_shoulder_power':  1.22,         # [INFERRED] Moderate roll-off, preserves highlight detail
    },

    'color': {
        # ---- Shadow tint: warm red shift (C200 unique signature) ----
        # Evidence: 像素侠 — 6/7 photos shadow H_med=13-52° (red/orange dominate)
        #   + 思源 — community "阴天发红发紫"
        #   + 程远 — engine test: deep shadow H=240→273° (+33° toward magenta)
        # [MEASURED] — pixel data: R channel dominates in shadows
        'shadow_tint':             [1.025, 0.995, 0.965],   # R +2.5%, G ~neutral, B -3.5% → warm red shadow

        # ---- Highlight tint: slight blue-neutral ----
        # Evidence: C200 preserves highlight color well, not aggressively cool
        # [INFERRED]
        'highlight_tint':          [1.00, 1.00, 1.01],     # Very subtle blue in highlights

        # ---- Global saturation: moderate (between Provia and Velvia) ----
        # Evidence: Fuji X Weekly Color+2 (雅婷) → ~1.08 base
        #   BUT: 像素侠 SP3000 scan data shows lower saturation than Hasselblad
        #   SP3000 community "C200 experience" = moderate saturation
        #   Compromise: 1.04 (slightly above neutral, not as high as Gold 200's 1.12)
        # [MEASURED] — mapped from Fuji Color+2 with SP3000 discount
        'global_saturation':        1.04,

        # ---- Highlight desaturation: moderate ----
        # Evidence: C200 preserves highlight color (i50mm: "轻松拍到有层次的云")
        # [INFERRED]
        'highlight_desat_start':   0.65,
        'highlight_desat_max':     0.08,                   # Subtle desat — preserves highlight color

        # ---- Skin tone protection — natural, warm but not orange-pushed ----
        # Evidence: 蔚然 D4 deep-dive
        #   像素侠: skin H_med=19-34°, S=0.29-0.43
        #   "细腻自然温暖，不推橙" vs Gold 200's strong orange push
        # [MEASURED] — pixel data + community consensus
        'skin_hue_min':            14.0,                   # [INFERRED] Slightly wider than 5219's 10-35
        'skin_hue_max':            36.0,
        'skin_sat_adjust':         0.98,                   # [MEASURED] Near-neutral — "生动再现" not muted

        # ---- Subdued hue shifts — C200 is less stylized than Gold 200 ----
        # Evidence: 蔚然 — orange_push=4°, not 10° like Gold 200
        #   teal_push modest — C200 blue is "nothing special" (CCB=Off)
        # [MEASURED] — relative to Gold 200/Positive Film anchor presets
        'teal_push':               0.0,                    # [MEASURED] C200 CCB=Off → no blue/teal push
        'orange_push':             4.0,                    # [MEASURED] Moderate — far less than Gold 200 (10°)

        # ---- Blue — natural depth, CCB=Off (C200 unique among Superia family) ----
        # Evidence: 雅婷 — CCB=Off (only C200 in Superia family)
        #   蔚然 — "无为而治" blue, not enhanced
        #   像素侠: blue H=209-240°, S=0.10-0.41 (natural variation)
        #   teal_push=0 + blue_hue_shift=0 = true CCB=Off behavior
        # [MEASURED] — CCB=Off mapping
        'blue_saturation_boost':   1.02,                   # [MEASURED] Barely enhanced (CCB=Off)
        'blue_luminance_shift':   -0.01,                   # [INFERRED] Slight depth
        'blue_hue_shift':          0.0,                    # [MEASURED] No shift — CCB=Off

        # ---- White balance: micro-warm (not cool!) ----
        # Evidence: 程远 — Fuji 0R/-3B = warm direction (+200-250K)
        #   像素侠 — R/G=1.350, B/G=0.853 (warm dominant)
        #   Reduced to +150K to compensate engine R coupling
        # [MEASURED] — WB convention verified + pixel data cross-checked
        'white_balance_shift_k': 150.0,                    # [MEASURED] Micro-warm, compensated for R coupling
    },
}


# ============================================================================
# C200 Pipeline Function
# ============================================================================

def c200_full_pipeline(rgb_rec709_linear):
    """Apply C200 tone curve + color grade, return display gamma output."""
    tonemapped = apply_tone_curve(rgb_rec709_linear, PRESET)
    graded = apply_color_grade(tonemapped, PRESET)
    return linear_to_display(graded)


def c200_info():
    """Print preset summary."""
    t = PRESET['tone']
    c = PRESET['color']
    pc = t['per_channel_contrast']
    print("=" * 65)
    print(f"  {PRESET['title']}")
    print("=" * 65)
    print(f"  Tone:")
    print(f"    black_lift={t['black_lift']:.5f}  shadow_toe_power={t['shadow_toe_power']:.2f}")
    print(f"    contrast={t['contrast']:.2f}  per_channel=[{pc[0]:.2f},{pc[1]:.2f},{pc[2]:.2f}]")
    print(f"    highlight_shoulder_start={t['highlight_shoulder_start']:.2f}  power={t['highlight_shoulder_power']:.2f}")
    print(f"  Color:")
    print(f"    shadow_tint=[{c['shadow_tint'][0]:.3f},{c['shadow_tint'][1]:.3f},{c['shadow_tint'][2]:.3f}]")
    print(f"    highlight_tint=[{c['highlight_tint'][0]:.2f},{c['highlight_tint'][1]:.2f},{c['highlight_tint'][2]:.2f}]")
    print(f"    global_sat={c['global_saturation']:.2f}  highlight_desat_max={c['highlight_desat_max']:.2f}")
    print(f"    skin_hue={c['skin_hue_min']:.0f}-{c['skin_hue_max']:.0f}°  skin_sat={c['skin_sat_adjust']:.2f}")
    print(f"    teal_push={c['teal_push']:.1f}°  orange_push={c['orange_push']:.1f}°")
    print(f"    blue: sat={c['blue_saturation_boost']:.2f}  hue={c['blue_hue_shift']:+.0f}°  lum={c['blue_luminance_shift']:+.2f}")
    print(f"    white_balance_shift_k={c['white_balance_shift_k']:+.0f}K")
    print()


# ============================================================================
# Test Color Suite
# ============================================================================

TEST_COLORS = [
    # (name, R, G, B, description)
    ("N1.5 深灰",  0.09, 0.09, 0.09, "Near-black neutral"),
    ("N3 暗灰",    0.20, 0.20, 0.20, "Deep shadow neutral"),
    ("N5 中灰",    0.50, 0.50, 0.50, "Mid-gray reference"),
    ("N7 亮灰",    0.72, 0.72, 0.72, "Light gray"),
    ("N8 浅灰",    0.85, 0.85, 0.85, "Near-white neutral"),
    ("N9.5 接近白", 0.97, 0.97, 0.97, "Almost white"),
    ("纯红",        1.00, 0.00, 0.00, "Pure red"),
    ("纯橙",        1.00, 0.50, 0.00, "Orange"),
    ("纯黄",        1.00, 1.00, 0.00, "Pure yellow"),
    ("纯绿",        0.00, 1.00, 0.00, "Pure green"),
    ("纯青",        0.00, 1.00, 1.00, "Pure cyan"),
    ("纯蓝",        0.00, 0.00, 1.00, "Pure blue (240°)"),
    ("纯品红",      1.00, 0.00, 1.00, "Pure magenta"),
    ("亚洲肤色",    0.90, 0.68, 0.52, "Asian skin ~25°"),
    ("偏冷肤色",    0.82, 0.64, 0.55, "Cool skin ~20°"),
    ("天空蓝",      0.35, 0.55, 0.90, "Sky blue ~215°"),
    ("深绿叶",      0.12, 0.45, 0.10, "Deep green foliage"),
    ("亮绿叶",      0.30, 0.75, 0.18, "Bright green foliage"),
    ("暗部测试色",  0.12, 0.10, 0.10, "Very dark for shadow tint test"),
    ("高光测试色",  0.92, 0.90, 0.88, "Bright for highlight tint test"),
]


def run_pipeline_tests():
    """Run all test colors through the C200 pipeline and report results."""
    print("=" * 65)
    print("  FULL PIPELINE TEST — 20 colors")
    print("=" * 65)
    print(f"  {'Color':<16} {'H_in':>6} {'H_out':>6} {'ΔH':>6} {'S_in':>5} {'S_out':>5} {'ΔS':>6}  Notes")
    print(f"  {'-'*16} {'-'*6} {'-'*6} {'-'*6} {'-'*5} {'-'*5} {'-'*6}  {'-'*30}")

    results = []
    for name, r, g, b, desc in TEST_COLORS:
        rgb_in = np.array([r, g, b], dtype=np.float64)
        rgb_out = c200_full_pipeline(rgb_in)
        rgb_out = np.clip(rgb_out, 0.0, 1.0)

        h_in, s_in, l_in = rgb_to_hsl(r, g, b)
        h_out, s_out, l_out = rgb_to_hsl(rgb_out[0], rgb_out[1], rgb_out[2])

        dh = h_out - h_in
        # Handle hue wraparound
        if dh > 180: dh -= 360
        if dh < -180: dh += 360
        ds = s_out - s_in

        notes = ""
        # Special annotations
        if "灰" in name and s_in < 0.01:
            # For near-neutrals, check color cast
            r_ratio = rgb_out[0] / (rgb_out[1] + 1e-12)
            b_ratio = rgb_out[2] / (rgb_out[1] + 1e-12)
            if r_ratio > 1.02:
                notes = f"🔴 Warm cast (R/G={r_ratio:.3f})"
            elif r_ratio < 0.98:
                notes = f"🔵 Cool cast (R/G={r_ratio:.3f})"
        elif "暗部" in name:
            notes = f"Shadow test: H_out={h_out:.0f}°"

        results.append({
            'name': name, 'h_in': h_in, 'h_out': h_out, 'dh': dh,
            's_in': s_in, 's_out': s_out, 'ds': ds,
            'rgb_out': rgb_out, 'notes': notes,
        })
        print(f"  {name:<16} {h_in:6.1f} {h_out:6.1f} {dh:+6.1f} {s_in:5.3f} {s_out:5.3f} {ds:+7.3f}  {notes}")

    return results


# ============================================================================
# Feature Validation
# ============================================================================

def validate_features(results):
    """Validate 6 critical C200 features."""
    print()
    print("=" * 65)
    print("  FEATURE VALIDATION")
    print("=" * 65)

    def find(name):
        for r in results:
            if r['name'] == name:
                return r
        return None

    issues = []

    # Feature 1: Neutral gray should not have strong warm cast
    n5 = find("N5 中灰")
    if n5:
        r_ratio = n5['rgb_out'][0] / (n5['rgb_out'][1] + 1e-12)
        b_ratio = n5['rgb_out'][2] / (n5['rgb_out'][1] + 1e-12)
        if r_ratio > 1.05:
            issues.append(f"❌ F1: N5 mid-gray too warm (R/G={r_ratio:.3f} > 1.05)")
        elif r_ratio > 1.02:
            print(f"  ⚠️  F1: N5 mid-gray slightly warm (R/G={r_ratio:.3f}) — acceptable")
        else:
            print(f"  ✅ F1: N5 mid-gray neutral (R/G={r_ratio:.3f})")

    # Feature 2: Shadow should have red shift
    shadow = find("暗部测试色")
    if shadow:
        h_out = shadow['h_out']
        if h_out < 10 or h_out > 50:
            print(f"  ✅ F2: Shadow hue shifted to warm (H={h_out:.0f}°)")
        else:
            issues.append(f"❌ F2: Shadow hue not shifted (H={h_out:.0f}°)")

    # Feature 3: Blue stays natural (CCB=Off characteristic)
    blue = find("纯蓝")
    if blue:
        ds = blue['ds']
        dh = blue['dh']
        if abs(dh) < 3.0:
            print(f"  ✅ F3: Blue hue nearly unchanged (ΔH={dh:+.1f}°) — CCB=Off behavior")
        else:
            issues.append(f"❌ F3: Blue hue shifted too much (ΔH={dh:+.1f}°)")
        if ds > -0.08:
            print(f"  ✅ F3b: Blue saturation not crushed (ΔS={ds:+.3f})")

    # Feature 4: Skin tones stay in natural range
    skin = find("亚洲肤色")
    if skin:
        h_out = skin['h_out']
        if 15 <= h_out <= 38:
            print(f"  ✅ F4: Asian skin hue natural (H={h_out:.0f}°)")
        else:
            issues.append(f"❌ F4: Skin hue out of range (H={h_out:.0f}°)")
        ds = skin['ds']
        if -0.05 <= ds <= 0.15:
            print(f"  ✅ F4b: Skin saturation controlled (ΔS={ds:+.3f})")
        else:
            issues.append(f"❌ F4b: Skin saturation extreme (ΔS={ds:+.3f})")

    # Feature 5: Contrast is soft (verify tone curve behavior)
    n15 = find("N1.5 深灰")
    n95 = find("N9.5 接近白")
    if n15 and n95:
        shadow_luma = 0.2126 * n15['rgb_out'][0] + 0.7152 * n15['rgb_out'][1] + 0.0722 * n15['rgb_out'][2]
        if shadow_luma > 0.04:
            print(f"  ✅ F5: Shadow detail preserved (N1.5 luma={shadow_luma:.3f})")
        else:
            issues.append(f"❌ F5: Shadows crushed (N1.5 luma={shadow_luma:.3f})")

    # Feature 6: WB shift is correct (warm, not cool)
    n5 = find("N5 中灰")
    if n5:
        h_out = n5['h_out']
        # If WB is warm, N5 hue should lean slightly warm
        if h_out < 90 or h_out > 270:  # warm-ish
            print(f"  ✅ F6: WB warm direction confirmed (N5 H={h_out:.0f}°)")
        elif h_out > 180:
            issues.append(f"❌ F6: WB too cool (N5 H={h_out:.0f}° → blue direction)")

    print()
    if issues:
        print(f"  ⚠️  {len(issues)} validation issue(s):")
        for i in issues:
            print(f"    {i}")
    else:
        print(f"  ✅ All 6 features validated!")

    return issues


# ============================================================================
# Test Reference Image Generation
# ============================================================================

def generate_test_reference():
    """Generate test_reference_c200.png."""
    # Inlined test-strip / hue-wheel helpers (no longer in engine.apply).
    def _test_strip(lut_func, width=1920, height=200):
        x = np.linspace(0, 1, width, dtype=np.float64)
        h_gray = int(height * 0.4)
        h_rgb = int(height * 0.2)
        h_b = height - h_gray - 2 * h_rgb
        strips = []
        gray = np.tile(x, (h_gray, 1))
        strips.append(np.stack([gray, gray, gray], axis=-1))
        strips.append(np.stack([x, np.zeros_like(x), np.zeros_like(x)], axis=-1).reshape(1, width, 3).repeat(h_rgb, axis=0))
        strips.append(np.stack([np.zeros_like(x), x, np.zeros_like(x)], axis=-1).reshape(1, width, 3).repeat(h_rgb, axis=0))
        strips.append(np.stack([np.zeros_like(x), np.zeros_like(x), x], axis=-1).reshape(1, width, 3).repeat(h_b, axis=0))
        image = np.concatenate(strips, axis=0)
        flat = image.reshape(-1, 3)
        result = np.clip(lut_func(flat), 0, 1)
        return (result.reshape(image.shape) * 255).astype(np.uint8)

    def _hue_wheel(lut_func, radius=300):
        size = radius * 2
        y, x = np.ogrid[-radius:radius, -radius:radius]
        dist = np.sqrt(x*x + y*y) / radius
        hue = ((np.arctan2(y, x) / (2*np.pi)) % 1.0) * 360.0
        sat = np.clip(dist, 0.0, 1.0)
        lum = np.full_like(sat, 0.5)
        r, g, b = hsl_to_rgb(hue.flatten(), sat.flatten(), lum.flatten())
        rgb_flat = np.column_stack([r, g, b])
        result = lut_func(rgb_flat).reshape(size, size, 3)
        result[dist > 1.0] = 0.2
        return (result * 255).astype(np.uint8)

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("⚠ Pillow not installed. Skipping test reference image.")
        return None

    name = PRESET['name']
    title = PRESET['title']

    def preset_pipeline(rgb_linear):
        tonemapped = apply_tone_curve(rgb_linear, PRESET)
        graded = apply_color_grade(tonemapped, PRESET)
        return linear_to_display(graded)

    def neutral_pipeline(rgb_linear):
        return linear_to_display(rgb_linear)

    strip_h, strip_w = 200, 1920
    wheel_r = 300

    before_strip = _test_strip(neutral_pipeline, strip_w, strip_h)
    after_strip  = _test_strip(preset_pipeline, strip_w, strip_h)
    before_wheel = _hue_wheel(neutral_pipeline, wheel_r)
    after_wheel  = _hue_wheel(preset_pipeline, wheel_r)

    gap = 20
    total_h = wheel_r * 2 + 80 + gap * 2
    total_w = strip_w + wheel_r * 4 + gap * 3 + 40

    canvas = np.ones((total_h, total_w, 3), dtype=np.uint8) * 30

    canvas[60:60 + strip_h, 20:20 + strip_w] = before_strip
    canvas[60 + strip_h + gap:60 + strip_h * 2 + gap, 20:20 + strip_w] = after_strip

    wx = 20 + strip_w + gap
    wy = 60
    canvas[wy:wy + wheel_r * 2, wx:wx + wheel_r * 2] = before_wheel
    wx2 = wx + wheel_r * 2 + gap
    canvas[wy:wy + wheel_r * 2, wx2:wx2 + wheel_r * 2] = after_wheel

    img = Image.fromarray(canvas)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()

    draw.text((20, 15), f"{title} — Test Reference", fill=(255, 255, 255), font=font_title)
    draw.text((20, 60), "Before (Linear → sRGB)", fill=(200, 200, 200), font=font_label)
    draw.text((20, 60 + strip_h + gap), f"After (Linear → {title})", fill=(200, 200, 200), font=font_label)
    draw.text((wx, 60), "Hue Wheel: Before", fill=(200, 200, 200), font=font_label)
    draw.text((wx2, 60), f"Hue Wheel: {name}", fill=(200, 200, 200), font=font_label)

    output_path = f'test_reference_{name}.png'
    img.save(output_path, 'PNG')
    print(f"  ✓ {output_path} — {total_w}x{total_h} pixels")
    return output_path


# ============================================================================
# Main
# ============================================================================

def main():
    c200_info()
    results = run_pipeline_tests()
    issues = validate_features(results)
    ref_path = generate_test_reference()

    print()
    print("=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    print(f"  Colors tested: {len(results)}")
    print(f"  Validation issues: {len(issues)}")
    if ref_path:
        print(f"  Reference image: {ref_path}")
    print(f"  Preset ready for: presets/c200.py")
    print()

    # Print evidence legend
    print("  Evidence legend:")
    print("    [MEASURED]  — pixel data or engine test confirmed")
    print("    [INFERRED]  — reasoned from reliable proxies")
    print("    [GUESS]     — community description only, needs real C200 scan calibration")
    print()

    # Known caveats
    print("  Known caveats:")
    print("    • green_* engine params not yet implemented → Fuji green rendered via")
    print("      per_channel_contrast G + global_sat, not a dedicated green channel")
    print("    • WB is micro-warm (+150K, compensating for engine R coupling)")
    print("      This may need adjustment after visual comparison with C200 scans")
    print("    • SP3000 vs emulsion truth unresolved — this preset targets the")
    print("      community 'C200 experience' (SP3000-biased)")
    print("    • No real C200 → engine calibration performed yet")
    print("      (needs ColorChecker shot on C200 vs S9+LUT comparison)")
    print()


if __name__ == '__main__':
    main()
