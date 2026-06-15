"""
Leica M9 CCD Day — Panasonic S9 V-Log LUT
==========================================

M9 CCD-inspired daylight/street look for Panasonic S9 Real Time LUT.
Built from public M9/M9-P/M-E sample observations and community consensus:
- low-ISO CCD clarity and firm midtone contrast
- dense but non-neon greens, slightly yellow/olive biased
- deep subdued blue skies
- rich reds/yellows with protected skin tones
- very light cyan bias in shadows

This is an inspired look, not a measured camera match.
Intended input: Panasonic S9 V-Log / V-Gamut.
Output: Rec.709 display look for in-camera/LUMIX Lab use.
"""

PRESET = {
    'name': 'm9_ccd_day',
    'title': 'Leica M9 CCD Day — S9 V-Log v1',
    'skip_standard': True,

    'tone': {
        # Clean, punchy low-ISO CCD contrast. Blacks are firm but not clipped.
        'black_lift':                0.0010,
        'shadow_toe_pivot':          0.09,
        'shadow_toe_power':          0.88,
        'contrast':                  1.11,
        'per_channel_contrast':      [1.01, 1.00, 1.03],
        'highlight_shoulder_start':  0.66,
        'highlight_shoulder_power':  1.26,
    },

    'color': {
        # Slight cyan in shadows, mildly warm highlights: restrained CCD split tone.
        'shadow_tint':             [0.985, 1.005, 1.030],
        'highlight_tint':          [1.020, 1.005, 0.985],
        'global_saturation':        1.08,
        'highlight_desat_start':   0.66,
        'highlight_desat_max':     0.10,

        # Avoid Leica/M9 red faces while preserving warm skin.
        'skin_hue_min':            12.0,
        'skin_hue_max':            38.0,
        'skin_sat_adjust':         0.92,

        # Keep hue moves subtle; dedicated blue/green controls carry the signature.
        'teal_push':               1.5,
        'orange_push':             3.0,

        # Deep, subdued M9 blue rather than modern electric cyan.
        'blue_saturation_boost':   1.04,
        'blue_luminance_shift':   -0.045,
        'blue_hue_shift':          1.0,

        # M9 green target: dense yellow-green/olive, not fluorescent.
        'green_saturation_boost':  0.96,
        'green_luminance_shift':  -0.025,
        'green_hue_shift':        -5.0,

        # Slight daylight warmth.
        'white_balance_shift_k':  220.0,
    },
}
