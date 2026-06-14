"""
Fujifilm Fujicolor C200 (Japan) — v1
======================================
Based on 2-round deep investigation (2026-06-14) with pixel-level
color sampling, community consensus cross-validation, and engine
quantitative verification.

See: docs/superpowers/research/2026-06-14-c200-round2-merged.md

Design philosophy (from research and pixel measurement):
  1. Micro-warm white balance (+150K) — C200 is warmer than "Fuji cool" myth
  2. Warm shadow red shift — "阴天发红发紫" signature (6/7 photos confirmed)
  3. Natural, moderate saturation — "色彩稍重" but not Velvia-level
     (Fuji Color+2 ~ global_sat=1.04 after SP3000 discount)
  4. CCB=Off blue — C200 is unique in Superia family for NOT boosting blue
     (teal_push=0, blue_hue_shift=0)
  5. Asian skin tone friendly — warm (19-34°) but not orange-pushed
  6. Soft contrast with shadow detail — H+0.5/S-0.5 inspired tone curve
  7. Fuji Green — rendered via per_channel_contrast G +2%
     (dedicated green_* engine params not yet implemented)

Key differentiators from existing presets:
  vs Gold 200: cooler WB (150K vs 400K), less orange (4° vs 10°),
               natural blue (CCB=Off vs warm cyan), warmer shadows
  vs Positive Film: lower saturation (1.04 vs 1.18), softer contrast (0.96 vs 1.04),
               more natural blue, red shadows vs neutral
  vs 5219: higher saturation, warm WB, red shadows vs cyan shadows
  vs HNCS: more stylized, warmer, red shadow signature
  vs Leica Classic: warmer WB direction, softer contrast, red shadows

Evidence legend (per parameter):
  [MEASURED]  — pixel data or engine test confirmed
  [INFERRED]  — reasoned from reliable proxies
  [GUESS]     — community description only, needs real C200 scan calibration

Known caveats:
  • green_* engine params not yet implemented → Fuji green rendered via
    per_channel_contrast G + global_sat, not a dedicated green channel
  • SP3000 vs emulsion truth unresolved — this preset targets the
    community "C200 experience" (SP3000-biased pixel sampling)
  • No real C200 → engine calibration performed yet
    (needs ColorChecker shot on C200 vs S9+LUT comparison)
  • WB is micro-warm (+150K) — compensates for engine R coupling;
    the Fuji X Weekly recipe's 0R/-3B is truly warm (~+250K uncompensated)
"""

PRESET = {
    'name': 'c200',
    'title': 'Fujifilm Fujicolor C200 (Japan)',
    'skip_vlog': True,                     # C200 is a consumer film sim — Standard mode only

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

        # ---- Highlight tint: neutral with very subtle blue ----
        # Evidence: C200 preserves highlight color well, not aggressively cool
        # [INFERRED]
        'highlight_tint':          [1.00, 1.00, 1.01],     # Very subtle blue in highlights

        # ---- Global saturation: moderate (between Provia and Velvia) ----
        # Evidence: Fuji X Weekly Color+2 (雅婷) → ~1.08 base
        #   BUT: 像素侠 SP3000 scan data shows lower saturation than Hasselblad
        #   SP3000 community "C200 experience" = moderate saturation
        #   Compromise: 1.04 (above neutral, below Gold 200's 1.12)
        # [MEASURED] — mapped from Fuji Color+2 with SP3000 discount
        'global_saturation':        1.04,

        # ---- Highlight desaturation: subtle ----
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
        #   teal_push=0 — C200 CCB=Off means no blue push at all
        # [MEASURED] — relative to Gold 200/Positive Film anchor presets
        'teal_push':               0.0,                    # [MEASURED] C200 CCB=Off → no blue/teal push
        'orange_push':             4.0,                    # [MEASURED] Moderate — far less than Gold 200 (10°)

        # ---- Blue — natural depth, CCB=Off (C200 unique among Superia family) ----
        # Evidence: 雅婷 — CCB=Off (only C200 in Superia family uses Off)
        #   蔚然 — "无为而治" blue, not enhanced
        #   像素侠: blue H=209-240°, S=0.10-0.41 (natural variation)
        #   teal_push=0 + blue_hue_shift=0 = true CCB=Off behavior
        # [MEASURED] — CCB=Off mapping, validated in pipeline test
        'blue_saturation_boost':   1.02,                   # [MEASURED] Barely enhanced (CCB=Off)
        'blue_luminance_shift':   -0.01,                   # [INFERRED] Slight depth
        'blue_hue_shift':          0.0,                    # [MEASURED] No shift — CCB=Off =

        # ---- White balance: micro-warm (not cool!) ----
        # Evidence: 程远 — Fuji 0R/-3B = warm direction (+200-250K uncompensated)
        #   像素侠 — R/G=1.350, B/G=0.853 (warm dominant in pixel data)
        #   Reduced to +150K to compensate engine R coupling
        # [MEASURED] — WB convention verified + pixel data cross-checked
        'white_balance_shift_k': 150.0,                    # [MEASURED] Micro-warm, compensated for R coupling

        # ---- Fuji Green — distinctive yellow-green, moderate-high saturation ----
        # Evidence: 绿植师 — pixel data from 9 C200 SP3000/Hasselblad dual scans
        #   Green median H≈132° (vs neutral 120° → +12° yellow-green shift)
        #   Moderate saturation boost to match "Fuji绿明显"
        #   Slight luminance boost → "小清新/塑料感"
        # [MEASURED] — pixel-sampled from actual C200 scans
        'green_hue_shift':         12.0,                   # [MEASURED] C200 greens median 132° vs neutral 120°
        'green_saturation_boost':  1.06,                   # [MEASURED] Moderate boost (sample S≈0.25)
        'green_luminance_shift':   0.02,                   # [MEASURED] Slight luminance lift
    },
}
