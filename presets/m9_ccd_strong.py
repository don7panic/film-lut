"""
Leica M9 CCD Strong — Panasonic S9 V-Log LUT
============================================

Stronger M9 CCD-inspired daylight/street LUT for Panasonic S9 Real Time LUT.
Pushes the public-community M9 traits harder: thicker color, firm black level,
more midtone bite, deep blue, dense yellow-green/olive foliage, and a visible but
controlled cyan shadow bias.

Use at lower LUT strength if S9/LUMIX Lab allows intensity control.
Intended input: Panasonic S9 V-Log / V-Gamut.
Output: Rec.709 display look for in-camera/LUMIX Lab use.
"""

PRESET = {
    'name': 'm9_ccd_strong',
    'title': 'Leica M9 CCD Strong — S9 V-Log v1',
    'lut_name': 'Leica_m9_strong',
    'skip_standard': True,

    'tone': {
        # High CCD/slide-like punch. Designed for sun/street, not gentle portraits.
        'black_lift':                0.0005,
        'shadow_toe_pivot':          0.08,
        'shadow_toe_power':          0.92,
        'contrast':                  1.18,
        'per_channel_contrast':      [1.02, 1.00, 1.05],
        'highlight_shoulder_start':  0.63,
        'highlight_shoulder_power':  1.34,
    },

    'color': {
        # More visible M9-like shadow cyan vs warm highlights, still restrained.
        'shadow_tint':             [0.970, 1.010, 1.055],
        'highlight_tint':          [1.035, 1.010, 0.970],
        'global_saturation':        1.14,
        'highlight_desat_start':   0.64,
        'highlight_desat_max':     0.08,

        # Protect skin from the stronger red/yellow push.
        'skin_hue_min':            12.0,
        'skin_hue_max':            38.0,
        'skin_sat_adjust':         0.86,

        'teal_push':               2.0,
        'orange_push':             4.5,

        # Rich, darker M9 blue.
        'blue_saturation_boost':   1.10,
        'blue_luminance_shift':   -0.070,
        'blue_hue_shift':          1.5,

        # Dense green: yellow/olive hue, lower luminance, enough saturation via global sat.
        'green_saturation_boost':  0.98,
        'green_luminance_shift':  -0.045,
        'green_hue_shift':        -7.0,

        'white_balance_shift_k':  300.0,
    },
}
