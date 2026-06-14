"""
Kodak Gold 200 — Warm Golden Consumer Film
===========================================
Research-calibrated (2026-06-14) based on quantitative LUT analysis
cross-referenced with Fuji X Weekly recipe (Ritchie Roesch) and
Dehancer Gold 200 profile.

Gold 200 is Kodak's classic consumer-grade color negative film. It's known for:
  • Reds pushed toward orange/amber — THE signature Gold 200 trait
  • Yellows pop — the "Gold" in the name
  • Blues are warm, muted, slightly cyan — skies look nostalgic, never cold
  • Greens lean yellow-green — warm, golden foliage
  • Golden skin tones — warm, flattering, sun-kissed
  • Saturated colors, bright prints (FPP Store)
  • Overall warm golden cast with moderate contrast

v2 changes (2026-06-14):
  - blue_hue_shift: +5.0 → -5.0 (correct toward cyan, not magenta)
  - teal_push: -5.0 → 5.0 (push toward teal, not away)
  - blue_saturation_boost: 0.85 → 0.95 (reduce over-suppression)
  - white_balance_shift_k: 1000 → 400 (tame excessive global warmth)
  - skin_hue_max: 40 → 35 (exclude pure orange)
  - skin_sat_adjust: 1.10 → 0.95 (protect/smooth, not boost)
  - per_channel_contrast: B=0.96 → B=1.02 (blue layer has highest gamma)
  - global_saturation: 1.02 → 1.12 (Gold 200 is saturated)
  - highlight_desat_max: 0.04 → 0.12 (more natural film highlight roll-off)

Refs: Fuji X Weekly Gold 200 recipe (fujixweekly.com), Dehancer profile,
      FPP store description, film community reviews.
"""

PRESET = {
    'name': 'gold200',
    'title': 'Kodak Gold 200 (Warm Golden) v2',

    'tone': {
        'black_lift':                0.0020,       # Film base
        'shadow_toe_pivot':          0.10,
        'shadow_toe_power':          0.86,         # Gentle shadow lift
        'contrast':                  0.96,         # Moderate (ref: Fuji X Weekly H-2/S+1)
        'per_channel_contrast':      [1.00, 1.00, 1.02],  # B最高（三层乳剂最上层γ最高）
        'highlight_shoulder_start':  0.72,
        'highlight_shoulder_power':  1.20,         # Smooth roll-off
    },

    'color': {
        # Warm-golden split tone
        'shadow_tint':             [1.03, 1.01, 0.95],     # Warm shadows (red boost, blue cut)
        'highlight_tint':          [1.06, 1.02, 0.90],     # Golden-cream highlights (reduced from v1)
        'global_saturation':        1.12,                   # Gold 200 is saturated (ref: Fuji Color+3)
        'highlight_desat_start':   0.68,
        'highlight_desat_max':     0.12,                   # Natural film highlight roll-off

        # Skin tones: warm golden but protected
        'skin_hue_min':            12.0,
        'skin_hue_max':            35.0,                   # Standard range (exclude pure orange)
        'skin_sat_adjust':         0.95,                   # Protect/smooth skin (not boost)

        # Gold 200 signature: reds → orange, blues → warm cyan
        'teal_push':              5.0,                     # Push blues toward teal (warm cyan)
        'orange_push':            10.0,                    # Strong red → amber shift

        # ---- Gold 200 specific ----
        'blue_saturation_boost':   0.95,                   # Muted but present (was 0.85)
        'blue_luminance_shift':   -0.04,                   # Slightly deeper blues
        'blue_hue_shift':         -5.0,                    # Blues → cyan (负 = 向青)
        'white_balance_shift_k':  400.0,                   # Moderate warmth (was 1000)
    },
}
