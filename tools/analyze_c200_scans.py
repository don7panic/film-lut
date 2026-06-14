import numpy as np
from PIL import Image

def rgb_to_hsl_vec(r, g, b):
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    l = (mx + mn) / 2.0
    delta = mx - mn
    
    s = np.where(delta == 0, 0.0,
        np.where(l < 0.5, delta / (mx + mn + 1e-12),
                          delta / (2.0 - mx - mn + 1e-12)))
    
    h = np.zeros_like(delta)
    mask_r = (mx == r) & (delta > 0)
    mask_g = (mx == g) & (delta > 0)
    mask_b = (mx == b) & (delta > 0)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        h = np.where(mask_r, 60.0 * (((g - b) / delta) % 6.0), h)
        h = np.where(mask_g, 60.0 * (((b - r) / delta) + 2.0), h)
        h = np.where(mask_b, 60.0 * (((r - g) / delta) + 4.0), h)
    
    return h, s, l

print("=== SP3000 vs Hasselblad X5 — C200 Film Scan Color Analysis ===\n")

all_deltas = {'R': [], 'G': [], 'B': [], 'H': [], 'S': [], 'L': []}

for i in range(1, 10):
    path = f'output/c200_compare_{i:02d}.jpg'
    try:
        img = Image.open(path).convert('RGB')
        arr = np.array(img, dtype=np.float64)
        h, w, _ = arr.shape
        mid = w // 2
        
        left = arr[:, :mid, :] / 255.0
        right = arr[:, mid:, :] / 255.0
        
        results = {}
        for label, half in [('SP3000', left), ('Hasselblad', right)]:
            r, g, b = half[..., 0], half[..., 1], half[..., 2]
            hsl_h, hsl_s, hsl_l = rgb_to_hsl_vec(r, g, b)
            results[label] = {
                'R': float(np.nanmean(r)) * 255,
                'G': float(np.nanmean(g)) * 255,
                'B': float(np.nanmean(b)) * 255,
                'H': float(np.nanmean(hsl_h)),
                'S': float(np.nanmean(hsl_s)),
                'L': float(np.nanmean(hsl_l)),
            }
        
        sp = results['SP3000']
        hs = results['Hasselblad']
        
        for k in ['R', 'G', 'B', 'H', 'S', 'L']:
            all_deltas[k].append(sp[k] - hs[k])
        
        print(f"Img {i}: SP3K R={sp['R']:.0f} G={sp['G']:.0f} B={sp['B']:.0f} H={sp['H']:.1f}° S={sp['S']:.3f}")
        print(f"        Hass R={hs['R']:.0f} G={hs['G']:.0f} B={hs['B']:.0f} H={hs['H']:.1f}° S={hs['S']:.3f}")
        print(f"        Δ    R={sp['R']-hs['R']:+.0f}  G={sp['G']-hs['G']:+.0f}  B={sp['B']-hs['B']:+.0f}  H={sp['H']-hs['H']:+.1f}°  S={sp['S']-hs['S']:+.3f}\n")
        
    except Exception as e:
        print(f"Img {i}: ERROR: {e}\n")

print("========== AGGREGATE STATISTICS ==========")
for k in ['R', 'G', 'B', 'H', 'S', 'L']:
    vals = all_deltas[k]
    if vals:
        print(f"  Δ{k}: mean={np.mean(vals):+.3f}  median={np.median(vals):+.3f}  stdev={np.std(vals):.3f}  min={np.min(vals):+.3f}  max={np.max(vals):+.3f}")

print("\n=== KEY FINDINGS ===")
print("Positive ΔR/ΔG/ΔB → SP3000 has MORE of that channel than Hasselblad")
print("Positive ΔH → SP3000 color is shifted clockwise (redder)")
print("Positive ΔS → SP3000 is MORE saturated")
print("Positive ΔL → SP3000 is BRIGHTER")
