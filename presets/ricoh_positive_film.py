"""
Ricoh Positive Film (ポジフィルム調) — Draft v1
================================================
Based on community research: 8 Ricoh Recipes, RGB curve analysis,
and official Image Control documentation.

⚠️ ALL VALUES ARE EDUCATED GUESSES — not yet calibrated against
   actual GR III RAW+JPEG pairs. Needs DCP analysis or in-camera
   RAW development for precise validation.

Design philosophy (from community analysis):
  1. Emulates color reversal film (slide film) — high saturation,
     punchy contrast, vibrant but not garish
  2. "Ricoh Blue" — deep, cyan-tinged blue channel boost
  3. Amber-warm reds with skin tone protection
  4. Compressed dynamic range: shadow lift + highlight shoulder
  5. Enhanced midtone contrast with lifted blacks for depth

See: docs/superpowers/research/2026-06-14-ricoh-final-report.md
"""

PRESET = {
    'name': 'ricoh_positive_film',
    'title': 'Ricoh Positive Film (ポジフィルム調)',
    'skip_standard': True,  # S9 Standard JPEG baseline differs from GR — V-Log only

    'tone': {
        # Compressed dynamic range: lifted blacks with controlled shadow detail
        # Community contrast(shadow) median: -3.5 → gentle shadow toe
        'black_lift':                0.0,          # No black floor — shadow_toe handles shadow lift naturally
        'shadow_toe_pivot':          0.08,
        'shadow_toe_power':          0.90,         # Very gentle shadow roll-off (was 0.87)
        'contrast':                  1.04,         # Punchy midtone but balanced brightness
        'per_channel_contrast':      [1.00, 1.00, 1.00],  # Uniform — blue character via color grade
        'highlight_shoulder_start':  0.65,         # Early shoulder for compressed highlights
        'highlight_shoulder_power':  1.30,         # Smooth highlight roll-off
    },

    'color': {
        # Neutral shadows, cool-bright highlights (blue-enhanced)
        'shadow_tint':             [1.00, 1.00, 1.00],     # Neutral shadows
        'highlight_tint':          [0.97, 0.98, 1.04],     # Cool highlight + blue boost
        'global_saturation':        1.18,                   # High saturation (signature)
        'highlight_desat_start':   0.65,
        'highlight_desat_max':     0.10,                   # Keep some color in highlights

        # Skin tone protection — prevents "pig liver red" at high saturation
        'skin_hue_min':            12.0,
        'skin_hue_max':            38.0,
        'skin_sat_adjust':         0.90,                   # Protect skin from oversaturation

        # Signature hue shifts: blue → cyan, red → amber
        'teal_push':               3.0,                    # Blue → cyan-tinged
        'orange_push':             6.0,                    # Red → warm amber

        # "Ricoh Blue" — deeper, richer, slightly cyan-shifted
        'blue_saturation_boost':   1.00,       # Neutral (was 1.08 — blue already boosted by global_sat + cool WB)
        'blue_luminance_shift':   0.0,         # Neutral (was -0.01 — zeroed dark blues)
        'blue_hue_shift':          2.0,        # Push blue toward cyan (was 4.0°)

        # Cool baseline (community: all recipes add Amber → baseline is cool)
        'white_balance_shift_k': -200.0,   # Cool baseline (was +300K — wrong direction)
    },
}
