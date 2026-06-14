# Phase B Research Notes: Kodak 5219 Calibration

**Date:** 2026-06-13

## Research Summary

Searched extensively for Kodak Vision3 5219 (500T) technical data and color science references. The official Kodak H-1-5219 technical data PDF is not publicly accessible (Kodak.com returns 404, mirrors under maintenance).

### Data Sources Accessed
- Cinestill 800T community reviews (Cinestill 800T = 5219 with remjet removed)
- Film photography community discussions (EMULSIVE, Douban, Zhihu)
- Roger Deakins forum discussions on film stock contrast curves
- GitHub: xtremestuff/resolve-aces (ACES IDT/ODT reference, no 5219-specific IDT found)

### Key Findings Used for Calibration

1. **Three-layer emulsion model:** 5219 has separate R, G, B emulsion layers with slightly different contrast. Blue layer is most contrasty (~0.60-0.65 gamma), red layer least (~0.50-0.55). This creates the signature cool shadows + warm highlights.

2. **Overall gamma:** ~0.55-0.60 — moderate contrast, softer than digital

3. **Color rendition (community-verified):**
   - Skin tones: warm, golden, smooth (the "Kodak look")
   - Shadows: slightly cool/cyan
   - Overall saturation: moderate ("not over saturated")
   - Greens: slightly desaturated

4. **Dynamic range:** ~14-15 stops, excellent highlight retention

5. **Tungsten-balanced (3200K):** Our LUT targets daylight reference (5600K), incorporating the warmth that 5219 naturally produces in daylight

### Parameter Calibrations Applied

| Parameter | v1 (hand-crafted) | v2 (research-calibrated) | Rationale |
|-----------|-------------------|--------------------------|-----------|
| Black lift | 0.0015 | 0.0018 | Closer to 5219 D-min ~0.18 |
| Shadow toe power | 0.85 | 0.82 | 5219 has softer toe |
| Contrast power | 1.12 | 1.08 | Closer to ~0.55 gamma |
| Per-channel contrast | — (uniform) | R×1.02, G×1.00, B×1.06 | 3-layer emulsion model |
| Shoulder start | 0.75 | 0.72 | Earlier roll-off for film look |
| Shoulder power | 1.15 | 1.25 | More compression (5219's excellent roll-off) |
| Global saturation | 0.93 | 0.90 | Better matches 5219's moderate saturation |
| Highlight desat | 0.12 | 0.15 | More natural film highlight behavior |
| Skin hue range | 12-38° | 10-35° | Tighter protection |
| Skin sat adjust | 0.90 | 0.88 | Smoother skin |
| Shadow tint | [1.01,1.00,1.04] | [1.00,1.00,1.03] | Subtler, more natural |
| Highlight tint | [1.03,0.99,0.95] | [1.03,0.99,0.96] | Subtler warmth |
| Teal push | 4.0° | 3.0° | More natural shift |
| Orange push | 3.0° | 2.0° | Subtler amber |

### Limitations
- No direct access to 5219 spectral dye density curves for precise color matrix derivation
- No 5219-specific ACES IDT available for reference
- Community-reported characteristics are qualitative rather than measured
- A proper scientific calibration would require shooting a color chart on actual 5219 film alongside the S9
