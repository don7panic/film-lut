"""
Kodak Vision3 5219 (500T) — Research-Calibrated Preset
========================================================
Daylight-balanced, moderate intensity.
Signature: warm skin tones, cyan-biased shadows, 3-layer emulsion contrast.
"""

PRESET = {
    'name': '5219',
    'title': 'Kodak Vision3 5219 (500T)',

    'tone': {
        'black_lift': 0.0018,
        'shadow_toe_pivot': 0.12,
        'shadow_toe_power': 0.82,
        'contrast': 1.08,
        'per_channel_contrast': [1.02, 1.00, 1.06],  # R, G, B
        'highlight_shoulder_start': 0.72,
        'highlight_shoulder_power': 1.25,
    },

    'color': {
        'shadow_tint':         [1.00, 1.00, 1.03],
        'highlight_tint':      [1.03, 0.99, 0.96],
        'global_saturation':    0.90,
        'highlight_desat_start': 0.60,
        'highlight_desat_max':  0.15,
        'skin_hue_min':         10.0,
        'skin_hue_max':         35.0,
        'skin_sat_adjust':      0.88,
        'teal_push':            3.0,
        'orange_push':          2.0,
    },
}
