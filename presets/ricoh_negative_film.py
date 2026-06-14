"""
Ricoh Negative Film (ネガフィルム調) — Draft v1
================================================
Based on: 1 community recipe (1986 Negative), official description,
and inference from Positive Film characteristics.

⚠️ EXTREMELY SPECULATIVE — only 1 recipe reference. All values are
educated guesses. Needs actual GR III Negative Film samples for calibration.

Design philosophy (from official description):
  1. "褪色感" (faded feel) — low saturation simulating aged print photos
  2. "清晰色彩" (clear colors) — selective retention: blues and greens stay vivid
  3. "底片冲印照片" — warm yellow-green cast, lifted blacks
  4. Low contrast, gentle tonal transitions

Key differences from Positive Film:
  - Positive Film: high saturation, cool baseline, slide film vibrancy
  - Negative Film: low saturation, warm baseline, faded print nostalgia

Reference recipe — 1986 Negative (Effect: Negative Film):
  Sat: +4  Hue: -2  Key: -1  Contrast: +2  Cont(H): +2  Cont(S): -3
  WB: CT 6700K  WB Comp: B:10 G:8
  → Baseline saturation very low (+4 recipe offset → baseline ~ -3 to -4)
  → Baseline warm yellow-green (6700K + strong blue compensation → cool compensation on warm base)

See: docs/superpowers/research/2026-06-14-ricoh-final-report.md
"""

PRESET = {
    'name': 'ricoh_negative_film',
    'title': 'Ricoh Negative Film (ネガフィルム調)',
    'skip_standard': True,  # S9 Standard baseline incompatible with GR — V-Log only

    'tone': {
        # Low contrast with gentle shadow lift
        # Recipe: Contrast=+2, but this is on baseline → baseline contrast likely low
        # Cont(S): -3 → lighter shadows
        'black_lift':                0.0005,       # Minimal floor only (Positive Film lesson)
        'shadow_toe_pivot':          0.10,
        'shadow_toe_power':          0.80,         # Aggressive shadow lift (faded print = lifted blacks)
        'contrast':                  0.94,         # Low contrast (<1.0 boosts shadows/mids, softens overall)
        'per_channel_contrast':      [1.00, 1.00, 1.00],  # Uniform — warmth via WB, not channel bias
        'highlight_shoulder_start':  0.60,         # Earlier shoulder → compressed highlights
        'highlight_shoulder_power':  1.40,         # Strong highlight compression (protect faded look)
    },

    'color': {
        # Warm vintage split-tone: cyan shadows, warm highlights
        'shadow_tint':             [0.96, 1.00, 1.02],     # Subtle cool cyan shadow (film negative cast)
        'highlight_tint':          [1.02, 1.00, 0.96],     # Warm highlight (yellowed print aging)
        'global_saturation':        0.78,                   # Low saturation — "faded" look (vs PF 1.18)
        'highlight_desat_start':   0.50,                    # Earlier desaturation for faded highlights
        'highlight_desat_max':     0.15,                    # Moderate fade (was 0.25 — too washed out)

        # Skin tone — keep natural in faded context
        'skin_hue_min':            10.0,
        'skin_hue_max':            40.0,
        'skin_sat_adjust':         1.00,                   # No extra skin protection needed at low sat

        # Minimal hue pushes — Negative Film is about subtlety, not stylization
        'teal_push':               0.0,                    # No teal push — blue stays natural
        'orange_push':             0.0,                    # No orange push — warm comes from WB, not hue shift

        # Blue/Green retention — "clear colors" amid fading
        # Blues stay relatively vivid even as warm tones fade
        'blue_saturation_boost':   1.12,                   # Boost blue to compensate for low global sat
        'blue_luminance_shift':    0.0,                    # Safe — no luminance shift (Positive Film lesson)
        'blue_hue_shift':          0.0,                    # Natural blue hue

        # Warm baseline: yellowish-green cast of aged prints
        # Recipe WB: CT 6700K + B:10 G:8 → baseline likely ~7500K+ (very warm/yellow)
        # Moderate warm shift — not as extreme as recipe compensation suggests
        'white_balance_shift_k':  400.0,                   # Warm vintage cast (was 600 — too warm midtones)
    },
}
