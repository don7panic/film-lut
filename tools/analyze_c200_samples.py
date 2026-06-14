"""Region-based color analysis of C200 sample photos from i50mm.com"""
import numpy as np
from PIL import Image
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.core import rgb_to_hsl

def sample_region(arr, x, y, w, h):
    """Sample a rectangular region and return mean HSL stats"""
    region = arr[y:y+h, x:x+w, :] / 255.0
    r, g, b = region[..., 0], region[..., 1], region[..., 2]
    hsv_h, hsv_s, hsv_l = rgb_to_hsl(r, g, b)
    return {
        'R': float(np.nanmean(r)*255), 'G': float(np.nanmean(g)*255), 'B': float(np.nanmean(b)*255),
        'H_mean': float(np.nanmean(hsv_h)), 'H_median': float(np.nanmedian(hsv_h)),
        'S_mean': float(np.nanmean(hsv_s)), 'L_mean': float(np.nanmean(hsv_l)),
        'pixels': w*h
    }

def analyze_c200_photo(path, label):
    """Analyze a C200 photo - global stats + look for visual characteristics"""
    img = Image.open(path).convert('RGB')
    arr = np.array(img, dtype=np.float64)
    h, w, _ = arr.shape
    
    # Global stats
    r, g, b = arr[..., 0]/255., arr[..., 1]/255., arr[..., 2]/255.
    hsl_h, hsl_s, hsl_l = rgb_to_hsl(r, g, b)
    
    # Luminance distribution
    shadows_pct = float(np.mean(hsl_l < 0.2) * 100)
    highlights_pct = float(np.mean(hsl_l > 0.8) * 100)
    midtones_pct = float(np.mean((hsl_l >= 0.2) & (hsl_l <= 0.8)) * 100)
    
    # Get overall color balance
    mean_r, mean_g, mean_b = float(np.nanmean(r))*255, float(np.nanmean(g))*255, float(np.nanmean(b))*255
    
    # Analyze hue distribution
    # Green region: 80-150°
    green_mask = (hsl_h >= 80) & (hsl_h <= 150)
    # Blue region: 200-260°
    blue_mask = (hsl_h >= 200) & (hsl_h <= 260)
    # Skin tone region: 10-40° (warm skin)
    skin_mask = (hsl_h >= 10) & (hsl_h <= 40) & (hsl_s > 0.05)
    
    result = {
        'label': label,
        'size': f'{w}x{h}',
        'global': {
            'R': mean_r, 'G': mean_g, 'B': mean_b,
            'H_mean': float(np.nanmean(hsl_h)), 'H_median': float(np.nanmedian(hsl_h)),
            'S_mean': float(np.nanmean(hsl_s)), 'L_mean': float(np.nanmean(hsl_l)),
            'R/G': mean_r/mean_g, 'B/G': mean_b/mean_g,
        },
        'luma_dist': {
            'shadows_0-20%': f'{shadows_pct:.1f}%',
            'midtones_20-80%': f'{midtones_pct:.1f}%',
            'highlights_80-100%': f'{highlights_pct:.1f}%',
        },
        'color_regions': {}
    }
    
    for name, mask in [('green(80-150°)', green_mask), ('blue(200-260°)', blue_mask), ('skin(10-40°)', skin_mask)]:
        if np.any(mask):
            result['color_regions'][name] = {
                'pixels_pct': f'{float(np.mean(mask))*100:.1f}%',
                'H_median': float(np.nanmedian(hsl_h[mask])),
                'S_mean': float(np.nanmean(hsl_s[mask])),
                'L_mean': float(np.nanmean(hsl_l[mask])),
            }
    
    # Shadow color analysis: what hue do dark pixels have?
    dark_mask = hsl_l < 0.25
    if np.any(dark_mask):
        result['shadow_color'] = {
            'pixels_pct': f'{float(np.mean(dark_mask))*100:.1f}%',
            'H_median': float(np.nanmedian(hsl_h[dark_mask])),
            'S_mean': float(np.nanmean(hsl_s[dark_mask])),
            'R_mean': float(np.nanmean(r[dark_mask]))*255,
            'G_mean': float(np.nanmean(g[dark_mask]))*255,
            'B_mean': float(np.nanmean(b[dark_mask]))*255,
        }
    
    return result

print("=" * 70)
print("FUJIFILM C200 SAMPLE PHOTO ANALYSIS (i50mm.com, Rollei 35)")
print("=" * 70)

all_global_h = []
all_rg = []
all_bg = []

for fname in sorted(os.listdir('output')):
    if not fname.startswith('c200_i50mm_'):
        continue
    path = os.path.join('output', fname)
    try:
        r = analyze_c200_photo(path, fname)
        all_global_h.append(r['global']['H_median'])
        all_rg.append(r['global']['R/G'])
        all_bg.append(r['global']['B/G'])
        
        g = r['global']
        print(f"\n--- {fname} ({r['size']}) ---")
        print(f"  Global:  R={g['R']:.0f} G={g['G']:.0f} B={g['B']:.0f} | H_med={g['H_median']:.0f}° S={g['S_mean']:.3f} L={g['L_mean']:.3f}")
        print(f"  R/G={g['R/G']:.3f}  B/G={g['B/G']:.3f}")
        print(f"  Luma:    {r['luma_dist']}")
        
        if 'shadow_color' in r:
            s = r['shadow_color']
            print(f"  Shadows: {s['pixels_pct']} pixels | H_med={s['H_median']:.0f}° S={s['S_mean']:.3f} | RGB=[{s['R_mean']:.0f},{s['G_mean']:.0f},{s['B_mean']:.0f}]")
        
        for name, cr in r['color_regions'].items():
            print(f"  {name}: {cr['pixels_pct']} pixels | H_med={cr['H_median']:.0f}° S={cr['S_mean']:.3f} L={cr['L_mean']:.3f}")
            
    except Exception as e:
        print(f"\n--- {fname} ERROR: {e}")

print("\n" + "=" * 70)
print("AGGREGATE STATISTICS (7 C200 photos from i50mm.com)")
print(f"  Median Hue:     mean={np.mean(all_global_h):.0f}°  stdev={np.std(all_global_h):.0f}°")
print(f"  R/G ratio:      mean={np.mean(all_rg):.4f}  stdev={np.std(all_rg):.4f}")
print(f"  B/G ratio:      mean={np.mean(all_bg):.4f}  stdev={np.std(all_bg):.4f}")
print(f"  B/G - R/G gap:  mean={np.mean(all_bg)-np.mean(all_rg):+.4f}")
print(f"\n  Interpretation:")
print(f"  R/G > 1 + B/G < R/G → warm/yellowish dominance (R stronger, B weaker)")
print(f"  B/G - R/G > 0 → cool cast; < 0 → warm cast")
