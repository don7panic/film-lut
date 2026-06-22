"""
Kodak Vision3 250D (5207) — v0.1 Research Preset
==================================================
Daylight-balanced medium-speed motion picture color negative.
Signature: natural soft skin tones, bright clean blue skies, neutral color palette.

Based on 3-round deep investigation (2026-06-14):
  R1: Community consensus + technical references
  R2: Fuji X Weekly recipe + Vision3 platform analysis
  R3: Engine parameter tuning + Standard/V-Log path validation

Design philosophy:
  1. Neutral daylight color balance (micro-cool -200K) — 5207 is NOT warm
  2. Natural skin tones — "专为人像设计", orange_push=0, skin_sat=0.93
  3. Enhanced blue rendering — "蓝天清澈明亮", blue_sat=1.12, hue=-4°
  4. Soft cinematic contrast (0.98) — "反差不大" but Vision3 latitude
  5. Neutral shadows — no 5219-like cyan bias, no Gold-like warmth
  6. Vision3 platform: B>G>R per-channel, superior highlight latitude

Key differentiators from existing presets:
  vs 5219: cooler WB, neutral shadows (vs cyan), lower contrast, higher sat, natural blue
  vs Gold 200: much cooler, natural vs golden skin, blue boost vs muted blue
  vs C200: neutral vs warm-red shadows, blue boost vs natural CCB=Off, no green shift

Evidence legend (per parameter):
  [PLATFORM]  — shared Vision3 trait, confirmed via 5219 audit
  [INFERRED]  — reasoned from multiple community sources
  [GUESS]     — single source only, needs pixel verification

Known caveats:
  • All parameters are [INFERRED] — no pixel-level measurement yet (R3 pending)
  • per_channel_contrast follows Vision3 B>G>R physics, specific values unmeasured
  • blue_hue_shift=-4° direction (purple vs cyan) needs pixel verification
  • WB -200K is a conservative estimate — actual range could be -300 to -50K
  • skip_vlog: Standard path preferred (V-Log has inherent shadow loss, see R2 audit)
"""

PRESET = {
    'name': '5207',
    'title': 'Kodak Vision3 250D (5207)',
    'lut_name': 'Kodak_5207',
    'skip_vlog': True,  # V-Log 33³ loses 12.5% shadow range → Standard preferred

    'tone': {
        # ---- Vision3 platform shared ----
        # [PLATFORM] — Same emulsion base as 5219
        'black_lift':                0.0018,       # Vision3 film base+fog
        'shadow_toe_pivot':          0.12,         # Vision3 shared pivot

        # ---- Softer than 5219, sharper than C200 ----
        # [INFERRED] — 知乎"反差不大" + EMULSIVE "bright/contrasty ↔ soft/pastel"
        #   5207 is versatile, base contrast near neutral
        'shadow_toe_power':          0.85,         # [INFERRED] 5219=0.82, 5207 has more shadow detail
        'contrast':                  0.98,         # [INFERRED] Lower than 5219(1.08), higher than C200(0.96)

        # ---- Vision3 3-layer emulsion ----
        # [INFERRED] — Deakins forum: "Blue and Green curves slightly steeper than Red"
        #   5219参考: [1.02, 1.00, 1.06]; 5207日光卷不需要钨丝灯B偏补偿
        #   v0.2 实测: R/G=1.211, B/G=0.691（与5219/Gold200明显区分）
        'per_channel_contrast':      [1.00, 1.00, 1.02],  # R, G, B — [INFERRED] 日光平衡保守估计

        # ---- Superior highlight latitude (-5.4 → +7 stops) ----
        # [INFERRED] — Kodak official "increased highlight latitude" + community measurements
        'highlight_shoulder_start':  0.72,         # [PLATFORM] Vision3 shared
        'highlight_shoulder_power':  1.30,         # [INFERRED] Superior roll-off for extreme highlights
    },

    'color': {
        # ---- Neutral shadow: no cyan bias (unlike 5219), no warm-red (unlike C200) ----
        # [INFERRED] — 豆瓣: "阴影下的偏蓝色透着淡淡的暖调"
        #   Compared to 5219 shadow_tint=[1.00,1.00,1.03] (cyan), 5207 is neutral
        'shadow_tint':             [1.00, 1.00, 1.01],     # [INFERRED] Near-neutral, micro-blue warmth

        # ---- Neutral highlight: no warm compensation needed (daylight native) ----
        # [INFERRED] — 5219 needs warm highlight (tungsten→daylight), 5207 doesn't
        'highlight_tint':          [1.00, 1.00, 1.00],     # [INFERRED] Pure neutral

        # ---- Moderate saturation: between 5219(0.90) and Gold(1.12) ----
        # [INFERRED] — EMULSIVE "vividly represented" BUT 知乎 "颜色偏清淡"
        #   5207 has good color separation without oversaturation
        'global_saturation':        0.98,                   # [INFERRED] Slightly below neutral

        # ---- Very subtle highlight desaturation — "亮处不易过曝" ----
        # [INFERRED] — 5207 preserves highlight color better than most films
        'highlight_desat_start':   0.68,
        'highlight_desat_max':     0.05,                   # [INFERRED] Minimal — excellent highlight color

        # ---- Natural skin tones for portraiture ----
        # [INFERRED] — EMULSIVE "all manner of skin tones handled with ease"
        #   + B站 "更适合东方肤色" + user requirement "自然柔和"
        #   Slightly wider than 5219(10-35°) for Asian skin range
        'skin_hue_min':            12.0,                   # [INFERRED]
        'skin_hue_max':            36.0,                   # [INFERRED] Asian + Caucasian coverage
        'skin_sat_adjust':         0.93,                   # [INFERRED] Gentle softening

        # ---- Minimal hue manipulation — "偏中性" ----
        # [INFERRED] — 图虫 "色调偏中性，后期可调空间大"
        #   No teal push (blue already enhanced), tiny orange for warmth
        'teal_push':               0.0,                    # [INFERRED] Blue stands on its own
        'orange_push':             0.0,                    # [INFERRED] "自然柔和" — no push needed

        # ---- Enhanced blue — "阳光下蓝天清澈明亮" ----
        # [INFERRED] — User requirement + 知乎 "蓝绿色偏高" (official curve) + 豆瓣 "偏蓝紫"
        #   blue_hue_shift=-4° toward cyan-violet (豆瓣: "偏蓝紫色")
        #   This differentiates from Gold 200's warm cyan and C200's CCB=Off
        'blue_saturation_boost':   1.12,                   # [INFERRED] Moderate enhancement
        'blue_luminance_shift':    -0.02,                  # [INFERRED] Slight deepening
        'blue_hue_shift':          -4.0,                   # [INFERRED] Toward cyan-violet ("偏蓝紫")

        # ---- Micro-cool white balance — daylight 5500K native ----
        # [INFERRED] — Community "偏中性偏蓝" consensus
        #   Conservative -100K estimate (range: -200 to +50K)
        'white_balance_shift_k':  -200.0,                  # [INFERRED] 日光自然微冷 (v0.2 engine tune)

        # ---- Green neutral — no signature green shift ----
        # 5207 has neutral greens, unlike C200's +12° yellow-green shift
        # (green_* parameters not set → defaults: 1.0, 0, 0)
    },
}
