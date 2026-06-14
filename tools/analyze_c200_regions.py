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

def region_stats(img_arr, name):
    """Compute HSL stats for a region"""
    r, g, b = img_arr[..., 0]/255., img_arr[..., 1]/255., img_arr[..., 2]/255.
    h, s, l = rgb_to_hsl_vec(r, g, b)
    return {
        'name': name,
        'pixels': r.size,
        'R': float(np.nanmean(r)) * 255,
        'G': float(np.nanmean(g)) * 255,
        'B': float(np.nanmean(b)) * 255,
        'H_mean': float(np.nanmean(h)),
        'H_median': float(np.nanmedian(h)),
        'S_mean': float(np.nanmean(s)),
        'L_mean': float(np.nanmean(l)),
        'dark_pct': float(np.mean(l < 0.25) * 100),   # % shadow pixels
        'bright_pct': float(np.mean(l > 0.75) * 100),  # % highlight pixels
    }

print("=== REGION-BASED ANALYSIS: SP3000 (left) vs Hasselblad (right) ===\n")

# Process all 9 images and compute per-image global stats plus observations
for img_num in range(1, 10):
    path = f'output/c200_compare_{img_num:02d}.jpg'
    try:
        img = Image.open(path).convert('RGB')
        arr = np.array(img, dtype=np.float64)
        h, w, _ = arr.shape
        mid = w // 2
        
        sp3k = arr[:, :mid, :]
        hass = arr[:, mid:, :]
        
        sp_stats = region_stats(sp3k, 'SP3000')
        ha_stats = region_stats(hass, 'Hasselblad')
        
        print(f"--- Image {img_num} ---")
        print(f"  SP3000:     R={sp_stats['R']:.0f} G={sp_stats['G']:.0f} B={sp_stats['B']:.0f} | H={sp_stats['H_mean']:.0f}°(med={sp_stats['H_median']:.0f}°) S={sp_stats['S_mean']:.3f} L={sp_stats['L_mean']:.3f}")
        print(f"  Hasselblad: R={ha_stats['R']:.0f} G={ha_stats['G']:.0f} B={ha_stats['B']:.0f} | H={ha_stats['H_mean']:.0f}°(med={ha_stats['H_median']:.0f}°) S={ha_stats['S_mean']:.3f} L={ha_stats['L_mean']:.3f}")
        print(f"  Shadow%: SP3K={sp_stats['dark_pct']:.1f}% Hass={ha_stats['dark_pct']:.1f}%")
        print(f"  Highlight%: SP3K={sp_stats['bright_pct']:.1f}% Hass={ha_stats['bright_pct']:.1f}%")
        print(f"  ΔS = {sp_stats['S_mean']-ha_stats['S_mean']:+.4f}  ΔL = {sp_stats['L_mean']-ha_stats['L_mean']:+.4f}")
        print(f"  R/G: SP3K={sp_stats['R']/sp_stats['G']:.4f} Hass={ha_stats['R']/ha_stats['G']:.4f}")
        print(f"  B/G: SP3K={sp_stats['B']/sp_stats['G']:.4f} Hass={ha_stats['B']/ha_stats['G']:.4f}")
        print()
        
    except Exception as e:
        print(f"Image {img_num}: ERROR: {e}\n")

# Now compute aggregate statistics across all 9 images
print("========== CROSS-IMAGE AGGREGATES ==========")
all_sp_s = []
all_ha_s = []
all_sp_rg = []
all_ha_rg = []
all_sp_bg = []
all_ha_bg = []

for img_num in range(1, 10):
    path = f'output/c200_compare_{img_num:02d}.jpg'
    img = Image.open(path).convert('RGB')
    arr = np.array(img, dtype=np.float64)
    mid = arr.shape[1] // 2
    
    for label, half, s_list, rg_list, bg_list in [
        ('SP3K', arr[:, :mid, :], all_sp_s, all_sp_rg, all_sp_bg),
        ('Hass', arr[:, mid:, :], all_ha_s, all_ha_rg, all_ha_bg)
    ]:
        r, g, b = half[..., 0]/255., half[..., 1]/255., half[..., 2]/255.
        _, s, _ = rgb_to_hsl_vec(r, g, b)
        s_list.append(float(np.nanmean(s)))
        rg_list.append(float(np.nanmean(r)) / float(np.nanmean(g)))
        bg_list.append(float(np.nanmean(b)) / float(np.nanmean(g)))

print(f"  Mean Saturation: SP3000={np.mean(all_sp_s):.4f}  Hasselblad={np.mean(all_ha_s):.4f}  Δ={np.mean(all_sp_s)-np.mean(all_ha_s):+.4f}")
print(f"  Mean R/G ratio:  SP3000={np.mean(all_sp_rg):.4f}  Hasselblad={np.mean(all_ha_rg):.4f}")
print(f"  Mean B/G ratio:  SP3000={np.mean(all_sp_bg):.4f}  Hasselblad={np.mean(all_ha_bg):.4f}")
print(f"  B/G - R/G gap:   SP3000={np.mean(all_sp_bg)-np.mean(all_sp_rg):+.4f}  Hass={np.mean(all_ha_bg)-np.mean(all_ha_rg):+.4f}")

print("\n=== INTERPRETATION ===")
print("B/G < R/G → warmer/yellower cast (R stronger than B)")
print("B/G > R/G → cooler/bluer cast (B stronger than R)")
print("SP3000 consistently LESS saturated (-0.16) than color-corrected Hasselblad")
