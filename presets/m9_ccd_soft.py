"""
Leica M9 CCD Soft — Panasonic S9 V-Log LUT
==========================================

Softer M9 CCD-inspired look for people, daily photos, mixed scenes.
Less contrast and safer skin than the Day/Strong versions; keeps the M9 direction
of warm reds, dense greens, and subdued blues without over-stylizing.

Intended input: Panasonic S9 V-Log / V-Gamut.
Output: Rec.709 display look for in-camera/LUMIX Lab use.
"""

PRESET = {
    'name': 'm9_ccd_soft',
    'title': 'Leica M9 CCD Soft — S9 V-Log v1',
    'lut_name': 'Leica_m9_soft',
    'skip_standard': True,

    'tone': {
        # Gentler contrast, more forgiving shadows/highlights for portraits.
        'black_lift':                0.0020,
        'shadow_toe_pivot':          0.10,
        'shadow_toe_power':          0.86,
        'contrast':                  1.05,
        'per_channel_contrast':      [1.00, 1.00, 1.01],
        'highlight_shoulder_start':  0.68,
        'highlight_shoulder_power':  1.22,
    },

    'color': {
        # Only a trace of M9 cyan-shadow separation.
        'shadow_tint':             [0.995, 1.002, 1.015],
        'highlight_tint':          [1.012, 1.003, 0.992],
        'global_saturation':        1.03,
        'highlight_desat_start':   0.64,
        'highlight_desat_max':     0.12,

        # Stronger skin protection than Day/Strong.
        'skin_hue_min':            10.0,
        'skin_hue_max':            40.0,
        'skin_sat_adjust':         0.88,

        'teal_push':               0.5,
        'orange_push':             2.0,

        # Blue depth is present but conservative.
        'blue_saturation_boost':   1.00,
        'blue_luminance_shift':   -0.025,
        'blue_hue_shift':          0.5,

        # Reduce modern green brightness; keep foliage natural.
        'green_saturation_boost':  0.90,
        'green_luminance_shift':  -0.015,
        'green_hue_shift':        -3.0,

        'white_balance_shift_k':  140.0,
    },
}
