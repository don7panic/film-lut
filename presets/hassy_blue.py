"""
Hasselblad HNCS — Natural Color Solution (Research-Calibrated v2)
==================================================================
Based on Hasselblad's official HNCS documentation and community analysis.
v2: Color audit corrections (2026-06-14) — see docs/superpowers/research/

HNCS philosophy (from Hasselblad's technical docs):
  1. "Hasselblad Film Curve" — perceptually-aware tone mapping is the SOUL of the look.
     Not a technical gamma, but a curve that enhances midtone contrast while keeping
     shadows and highlights smooth and natural.
  2. "Uncompromising skin tone reproduction" — skin stays natural even when curves
     and contrast are applied. This is the highest priority in HNCS.
  3. "Natural but better than accurate" — colors are perceptually enhanced beyond
     mere colorimetric accuracy, reflecting how the human eye experiences a scene.
  4. The signature "Hasselblad blue" is a RESULT of overall color accuracy + smooth
     tonality + natural skin — not from individually boosting the blue channel.
  5. Uses L*RGB (perceptually uniform, LAB-derived) color space internally for
     smooth, even color transitions.

Key adjustments (v2 audit corrections):
  • contrast > 1.0 — actually ENHANCES midtone contrast (was reducing it at 0.95)
  • WB shift reduced from -400K to -150K — subtle cool, not the main blue driver
  • blue_hue_shift removed — eliminates S-curve hue discontinuity in 200-270°
  • Skin tone range tightened — no longer extends into pure orange
  • Shadow tint slightly warm to balance overall cool profile
"""

PRESET = {
    'name': 'hassy_blue',
    'title': 'Hasselblad HNCS (Natural Color)',
    'lut_name': 'Hasselblad',
    'skip_vlog': True,  # V-Log path has shadow deadzone bug — Standard only

    'tone': {
        # "Hasselblad Film Curve" — perceptually enhanced midtone contrast
        'black_lift':                0.0040,       # Visible film base (8-bit: ~1)
        'shadow_toe_pivot':          0.12,
        'shadow_toe_power':          0.85,         # Smooth shadow roll-off (moderate toe)
        'contrast':                  1.08,         # > 1.0 enhances midtone contrast (was 0.95)
        'per_channel_contrast':      [1.00, 1.00, 1.00],  # Uniform — HNCS is chromatically neutral
        'highlight_shoulder_start':  0.68,
        'highlight_shoulder_power':  1.35,         # Stronger shoulder protection
    },

    'color': {
        # Neutral-clean split tone (HNCS doesn't do heavy split-toning)
        'shadow_tint':             [1.005, 1.00, 1.00],     # Subtle warm shadow balance
        'highlight_tint':          [1.00, 1.00, 1.00],     # Neutral highlights
        'global_saturation':        1.00,                   # Neutral — "natural but better than accurate"
        'highlight_desat_start':   0.62,
        'highlight_desat_max':     0.10,                   # Natural highlight roll-off

        # Skin tone — the highest priority in HNCS
        'skin_hue_min':            10.0,                   # Typical skin tone start
        'skin_hue_max':            38.0,                   # Not into pure orange (>40°)
        'skin_sat_adjust':         0.94,                   # Subtle skin smoothing

        # Minimal hue pushes — HNCS is about accuracy, not stylization
        'teal_push':               0.0,
        'orange_push':             0.0,

        # ---- Subtle HNCS blue characteristics ----
        # Blue emerges from overall accuracy + smooth tonality + clean WB — not channel boosting
        'blue_saturation_boost':   1.05,                   # Perceptible blue depth (+5%, net ~4% with WB)
        'blue_luminance_shift':   -0.02,                   # Deeper blues
        'blue_hue_shift':          0.0,                    # Removed — was causing S-curve discontinuity
        'white_balance_shift_k': -250.0,                   # Visible clean cool (was -400, then -150)
    },
}
