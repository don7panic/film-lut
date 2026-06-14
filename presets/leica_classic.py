"""
Leica Classic Look — Draft v1
==============================
Based on 3-round deep investigation of Leica color profiles (2026-06-14).
See: docs/superpowers/research/2026-06-14-leica-final-report.md

Intended for V-Log / V-Gamut input. The V-Log LUT handles:
  1. V-Log → scene-linear decoding
  2. V-Gamut → Rec.709 gamut conversion
  3. Leica Classic tone curve
  4. Leica Classic creative color grade
  5. Rec.709 display gamma encoding

Leica Classic is available across all three Leica color tiers:
  • Leica FOTOS app (downloadable to Q3/SL3)
  • Leica LUX iPhone app (Pro subscription)
  • Corresponds to Xiaomi "Leica Authentic" direction

Design philosophy (from community research and cross-referencing):
  1. Evokes classic Leica M film-era color — slightly warm, not clinical
  2. Medium-high contrast with rich shadow detail (Leica rarely crushes blacks)
  3. Deep, slightly cyan-tinged blues — the subtle "Leica blue" signature
  4. Rich but controlled reds — not pushed to orange like Gold 200
  5. Natural skin tones — "not pig-liver red" even at elevated contrast
  6. Smooth highlight roll-off with preserved color (Leica doesn't desaturate highlights aggressively)
  7. Subtle warm shadow cast — classic Leica warmth without yellow-green bias

Xiaomi "Leica Authentic" reference (closest publicly documented proxy):
  • High contrast, restrained saturation, cooler tone direction
  • Rich shadow detail with natural highlight preservation
  • "Purer Leica flavor" targeting street/documentary photography

Key differentiators from existing presets:
  vs HNCS: warmer, more contrast, distinctive blue-green character
  vs Gold 200: less golden/amber, blue stays deeper, more controlled warmth
  vs Positive Film: less saturated, more film-era restraint
  vs 5219: higher contrast + saturation, still-image look vs cinematic

⚠️ ALL VALUES ARE EDUCATED GUESSES based on community consensus and proxy data.
   Not yet calibrated against actual Leica Q3/SL3 Leica Looks output.
   Needs LUX app comparison or Xiaomi Authentic sample analysis for validation.
"""

PRESET = {
    'name': 'leica_classic',
    'title': 'Leica Classic Look — Draft v1',

    'tone': {
        # Medium-high contrast with preserved shadow detail
        # Leica's signature: punchy but not harsh, shadows have depth without crushing
        'black_lift':                0.0020,       # Slight film-base lift (Leica preserves blacks)
        'shadow_toe_pivot':          0.10,
        'shadow_toe_power':          0.84,         # Gentle shadow roll-off — detail in the dark
        'contrast':                  1.08,         # Medium-high punch (Leica signature)
        'per_channel_contrast':      [1.00, 0.98, 1.04],  # R neutral, G subtle, B strongest
        'highlight_shoulder_start':  0.68,         # Early shoulder — smooth highlight transition
        'highlight_shoulder_power':  1.30,         # Controlled roll-off, not aggressive
    },

    'color': {
        # Subtle warm shadows, clean highlights — classic Leica split-tone
        'shadow_tint':             [1.02, 1.00, 0.97],     # Warm shadow (red boost, blue slight cut)
        'highlight_tint':          [0.99, 1.00, 1.03],     # Cool-bright highlight (blue-enhanced)

        # Medium-high saturation — rich but controlled, not garish
        'global_saturation':        1.08,

        # Minimal highlight desaturation — Leica preserves color in bright areas
        'highlight_desat_start':   0.65,
        'highlight_desat_max':     0.08,

        # Skin tone protection — natural, not "pig-liver red"
        'skin_hue_min':            12.0,
        'skin_hue_max':            38.0,
        'skin_sat_adjust':         0.92,                   # Slight smoothing at high contrast

        # Subtle hue pushes — Leica Classic is restrained, not stylized
        'teal_push':               3.0,                    # Gentle blue → cyan (Leica blue signature)
        'orange_push':             4.0,                    # Subtle red → amber warmth

        # ---- Leica Blue — deep, rich, slightly cyan-tinged ----
        'blue_saturation_boost':   1.08,                   # Deeper, richer blues
        'blue_luminance_shift':   -0.03,                   # Darker blue luminance (depth)
        'blue_hue_shift':          3.0,                    # Push blue toward cyan (classic Leica)

        # Slightly warm daylight balance — classic Leica film-era warmth
        # More restrained than M9 CCD (~+500K), more present than modern M10
        'white_balance_shift_k':  300.0,
    },
}
