"""
Film LUT Engine — Color Science Core
=====================================
Shared color math: V-Log decoding, gamut conversion, tone curves,
creative color grading, and display gamma encoding.

All parameterized functions accept a ``params`` dict (loaded from presets).
"""

import numpy as np

# ============================================================================
# V-Log / V-Gamut Constants (Panasonic Varicam)
# ============================================================================

VLOG_CUT1 = 0.01
VLOG_B = 0.00873
VLOG_C = 0.241514
VLOG_D = 0.598206
VLOG_CROSSOVER = 5.6 * VLOG_CUT1 + 0.125  # ≈ 0.181


def vlog_to_linear(v):
    """Convert V-Log code value (0–1) to scene-linear light value.

    Inverse of Panasonic V-Log:
      If V < 0.181           → E = (V − 0.125) / 5.6
      Else                   → E = 10^((V − 0.598206) / 0.241514) − 0.00873
    """
    v = np.asarray(v, dtype=np.float64)
    linear = np.where(
        v < VLOG_CROSSOVER,
        (v - 0.125) / 5.6,
        np.power(10.0, (v - VLOG_D) / VLOG_C) - VLOG_B,
    )
    return np.clip(linear, 0.0, None)


def linear_to_vlog(linear):
    """Convert scene-linear to V-Log (forward direction). Used for validation.

      If E < 0.01 → V = 5.6·E + 0.125
      Else        → V = 0.241514·log10(E + 0.00873) + 0.598206
    """
    linear = np.asarray(linear, dtype=np.float64)
    vlog = np.where(
        linear < VLOG_CUT1,
        5.6 * linear + 0.125,
        VLOG_C * np.log10(linear + VLOG_B) + VLOG_D,
    )
    return np.clip(vlog, 0.0, 1.0)


# ============================================================================
# Color Space Conversion: V-Gamut → Rec.709
# ============================================================================

def _chromaticity_to_rgb_to_xyz_matrix(primaries, white_point):
    """Compute RGB→XYZ matrix from primaries and white point (CIE 1931 xy).

    Args:
        primaries: ((rx, ry), (gx, gy), (bx, by))
        white_point: (wx, wy)

    Returns:
        3×3 numpy array — RGB → XYZ matrix.
    """
    (rx, ry), (gx, gy), (bx, by) = primaries
    wx, wy = white_point

    rz = 1.0 - rx - ry
    gz = 1.0 - gx - gy
    bz = 1.0 - bx - by
    wz = 1.0 - wx - wy

    P = np.array([[rx, gx, bx], [ry, gy, by], [rz, gz, bz]], dtype=np.float64)
    W = np.array([wx / wy, 1.0, wz / wy], dtype=np.float64)
    S = np.linalg.solve(P, W)
    return P @ np.diag(S)


# Primaries
VGAMUT_PRIMARIES = ((0.730, 0.280), (0.165, 0.840), (0.100, -0.030))
REC709_PRIMARIES  = ((0.640, 0.330), (0.300, 0.600), (0.150, 0.060))
D65_WHITE         = (0.3127, 0.3290)

# Pre-computed matrices
_M_VGAMUT_TO_XYZ = _chromaticity_to_rgb_to_xyz_matrix(VGAMUT_PRIMARIES, D65_WHITE)
_M_REC709_TO_XYZ = _chromaticity_to_rgb_to_xyz_matrix(REC709_PRIMARIES, D65_WHITE)
M_VGAMUT_TO_REC709 = np.linalg.inv(_M_REC709_TO_XYZ) @ _M_VGAMUT_TO_XYZ


def vgamut_to_rec709(rgb):
    """Convert V-Gamut linear RGB → Rec.709 linear RGB.

    Handles 1-D (3,) and 2-D (N, 3) inputs transparently.
    """
    rgb = np.asarray(rgb, dtype=np.float64)
    if rgb.ndim == 1:
        return np.clip(M_VGAMUT_TO_REC709 @ rgb, 0.0, None)

    shape = rgb.shape
    flat = rgb.reshape(-1, 3)
    result = (M_VGAMUT_TO_REC709 @ flat.T).T
    return np.clip(result.reshape(shape), 0.0, None)


# ============================================================================
# Tone Curve – parameterized S-curve
# ============================================================================

def apply_tone_curve(linear_rgb, params):
    """Apply film-emulation S-curve in scene-linear space.

    Reads from ``params['tone']``:

    ========================  =============================================
    Key                       Meaning
    ========================  =============================================
    ``black_lift``            Minimum linear value (film base+fog)
    ``shadow_toe_pivot``      Where shadow compression ends
    ``shadow_toe_power``      < 1 lifts shadows (softer toe)
    ``contrast``              Base mid-tone contrast power
    ``per_channel_contrast``  [R, G, B] multipliers for 3-layer emulsion
    ``highlight_shoulder_start``  Where shoulder compression begins
    ``highlight_shoulder_power``  > 1 compresses highlights (roll-off)
    ========================  =============================================

    Handles 1-D (3,) and 2-D (N, 3) input arrays.
    """
    t = params['tone']
    black_lift                = t['black_lift']
    shadow_toe_pivot          = t['shadow_toe_pivot']
    shadow_toe_power          = t['shadow_toe_power']
    contrast_base             = t['contrast']
    per_channel               = np.asarray(t['per_channel_contrast'], dtype=np.float64)
    highlight_shoulder_start  = t['highlight_shoulder_start']
    highlight_shoulder_power  = t['highlight_shoulder_power']

    linear = np.asarray(linear_rgb, dtype=np.float64)
    shape = linear.shape
    if linear.ndim == 1:
        linear = linear.reshape(1, 3)

    # 1. Black floor lift
    linear = np.maximum(linear, black_lift)

    # 2. Shadow toe compression
    for c in range(3):
        mask = linear[:, c] < shadow_toe_pivot
        if np.any(mask):
            vals = linear[mask, c]
            t_vals = vals / shadow_toe_pivot
            linear[mask, c] = shadow_toe_pivot * (t_vals ** shadow_toe_power)

    # 3. Per-channel mid-tone contrast
    for c in range(3):
        ch_power = contrast_base * per_channel[c]
        linear[:, c] = linear[:, c] ** ch_power

    # 4. Highlight shoulder compression
    for c in range(3):
        mask = linear[:, c] > highlight_shoulder_start
        if np.any(mask):
            sv = linear[mask, c]
            s = (sv - highlight_shoulder_start) / (1.0 - highlight_shoulder_start)
            s_compressed = s ** highlight_shoulder_power
            linear[mask, c] = highlight_shoulder_start + s_compressed * (1.0 - highlight_shoulder_start)

    # 5. Re-normalize per sample, not across the whole LUT grid.
    # V-Log LUT generation feeds values far above display white into this function;
    # using a global max across the entire grid would crush all normal midtones.
    max_val = np.max(linear, axis=1, keepdims=True)
    over_range = max_val[:, 0] > 1.0
    if np.any(over_range):
        linear[over_range] = linear[over_range] / max_val[over_range]

    if len(shape) == 1:
        linear = linear[0]
    return linear


# ============================================================================
# HSL Helpers
# ============================================================================

def rgb_to_hsl(r, g, b):
    """Convert RGB (0–1) → HSL (H in [0, 360], S, L in [0, 1])."""
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    lum = (mx + mn) / 2.0

    delta = mx - mn
    sat = np.where(
        delta == 0, 0.0,
        np.where(lum < 0.5, delta / (mx + mn + 1e-12), delta / (2.0 - mx - mn + 1e-12)),
    )

    hue = np.zeros_like(delta)
    mask_r = (mx == r) & (delta > 0)
    mask_g = (mx == g) & (delta > 0)
    mask_b = (mx == b) & (delta > 0)
    with np.errstate(divide='ignore', invalid='ignore'):
        hue = np.where(mask_r, 60.0 * (((g - b) / delta) % 6.0), hue)
        hue = np.where(mask_g, 60.0 * (((b - r) / delta) + 2.0), hue)
        hue = np.where(mask_b, 60.0 * (((r - g) / delta) + 4.0), hue)

    return hue, sat, lum


def hsl_to_rgb(h, s, l):
    """Convert HSL → RGB. h in [0, 360], s, l in [0, 1]."""
    h = np.asarray(h, dtype=np.float64) % 360.0
    s = np.clip(np.asarray(s, dtype=np.float64), 0.0, 1.0)
    l = np.clip(np.asarray(l, dtype=np.float64), 0.0, 1.0)

    c = (1.0 - np.abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - np.abs((h / 60.0) % 2.0 - 1.0))
    m = l - c / 2.0

    h_sector = (h // 60).astype(int) % 6

    r1 = np.where((h_sector == 0) | (h_sector == 5), c,
                  np.where((h_sector == 1) | (h_sector == 4), x, 0.0))
    g1 = np.where((h_sector == 1) | (h_sector == 2), c,
                  np.where((h_sector == 0) | (h_sector == 3), x, 0.0))
    b1 = np.where((h_sector == 3) | (h_sector == 4), c,
                  np.where((h_sector == 2) | (h_sector == 5), x, 0.0))

    return r1 + m, g1 + m, b1 + m


# ============================================================================
# Creative Color Grade – parameterized
# ============================================================================

def apply_color_grade(linear_rgb, params):
    """Apply creative color grade in scene-linear RGB space.

    Reads from ``params['color']``:

    ===========================  ==========================================
    Key                          Meaning
    ===========================  ==========================================
    ``shadow_tint``              [R, G, B] multiplier in shadows
    ``highlight_tint``           [R, G, B] multiplier in highlights
    ``global_saturation``        Overall saturation scale (< 1 desaturates)
    ``highlight_desat_start``    Luminance where highlight desat begins
    ``highlight_desat_max``      Maximum desaturation at white
    ``skin_hue_min/max``         Skin-tone hue range (degrees)
    ``skin_sat_adjust``          Saturation multiplier for skin tones
    ``teal_push``                Hue shift for blues toward teal (deg)
    ``orange_push``              Hue shift for reds toward amber (deg)
    ``blue_saturation_boost``    *optional* extra saturation for 200–260°
    ``blue_luminance_shift``     *optional* luminance offset for blue hues
    ``blue_hue_shift``           *optional* hue offset for blue hues (deg)
    ``green_saturation_boost``   *optional* extra saturation for 85–155°
    ``green_luminance_shift``    *optional* luminance offset for green hues
    ``green_hue_shift``          *optional* hue offset for green hues (deg)
    ``white_balance_shift_k``    *optional* Kelvin-approximate WB shift
    ===========================  ==========================================

    Handles 1-D (3,) and 2-D (N, 3) input arrays.
    """
    C = params['color']
    shadow_tint    = np.asarray(C['shadow_tint'], dtype=np.float64)
    highlight_tint = np.asarray(C['highlight_tint'], dtype=np.float64)
    global_sat     = C['global_saturation']
    desat_start    = C['highlight_desat_start']
    desat_max      = C['highlight_desat_max']
    skin_min       = C['skin_hue_min']
    skin_max       = C['skin_hue_max']
    skin_sat_adj   = C['skin_sat_adjust']
    teal_push      = C['teal_push']
    orange_push    = C['orange_push']

    # Optional Hasselblad Blue / extended params
    blue_sat_boost   = C.get('blue_saturation_boost', 1.0)
    blue_lum_shift   = C.get('blue_luminance_shift', 0.0)
    blue_hue_shift   = C.get('blue_hue_shift', 0.0)
    green_sat_boost  = C.get('green_saturation_boost', 1.0)
    green_lum_shift  = C.get('green_luminance_shift', 0.0)
    green_hue_shift  = C.get('green_hue_shift', 0.0)
    wb_shift_k       = C.get('white_balance_shift_k', 0.0)

    rgb = np.asarray(linear_rgb, dtype=np.float64)
    shape = rgb.shape
    if rgb.ndim == 1:
        rgb = rgb.reshape(1, 3)

    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]

    # ---- Luminance (ITU-R BT.709) ----
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # ---- Step 1: Split-tone (shadow / highlight) ----
    shadow_w    = np.clip(1.0 - luma * 2.0, 0.0, 1.0)
    highlight_w = np.clip((luma - 0.5) * 2.0, 0.0, 1.0)
    mid_w       = 1.0 - shadow_w - highlight_w
    tint = (
        shadow_w[:, np.newaxis]    * shadow_tint +
        mid_w[:, np.newaxis]       * np.array([1.0, 1.0, 1.0]) +
        highlight_w[:, np.newaxis] * highlight_tint
    )
    r, g, b = r * tint[:, 0], g * tint[:, 1], b * tint[:, 2]

    # ---- Step 2: Optional white-balance shift (Kelvin approximation) ----
    if abs(wb_shift_k) > 0.001:
        # Warmer (positive K) → boost R, reduce B
        # Cooler (negative K) → boost B, reduce R
        factor = wb_shift_k / 10000.0
        r = r * (1.0 + factor)
        b = b * (1.0 - factor)

    # ---- Step 3: Convert to HSL ----
    h, s, l_hsl = rgb_to_hsl(r, g, b)

    # ---- Step 4: Global saturation ----
    s = s * global_sat

    # ---- Step 5: Highlight desaturation ----
    hd_mask = luma > desat_start
    if np.any(hd_mask):
        desat_factor = (luma[hd_mask] - desat_start) / (1.0 - desat_start)
        desat_factor = desat_factor * desat_max
        s[hd_mask] = s[hd_mask] * (1.0 - desat_factor)

    # ---- Step 6: Skin-tone protection ----
    skin_mask = (
        (h >= skin_min) & (h <= skin_max) &
        (s > 0.05) & (l_hsl > 0.15) & (l_hsl < 0.85)
    )
    s[skin_mask] = s[skin_mask] * skin_sat_adj

    # ---- Step 7: Teal / orange hue pushes ----
    blue_mask = (h >= 180.0) & (h <= 260.0)
    if teal_push != 0.0 and np.any(blue_mask):
        h[blue_mask] = h[blue_mask] + teal_push * np.sign(200.0 - h[blue_mask])

    red_mask = (h <= 40.0) | (h >= 350.0)  # 覆盖 0°/360° wraparound
    if orange_push != 0.0 and np.any(red_mask):
        h[red_mask] = (h[red_mask] + orange_push) % 360.0

    # ---- Step 8: Optional Hasselblad Blue channel boost ----
    if abs(blue_sat_boost - 1.0) > 0.001 or abs(blue_hue_shift) > 0.001 or abs(blue_lum_shift) > 0.001:
        blue_mask = (h >= 200.0) & (h <= 260.0)
        if np.any(blue_mask):
            s[blue_mask] = s[blue_mask] * blue_sat_boost
            h[blue_mask] = h[blue_mask] + blue_hue_shift
            l_hsl[blue_mask] = np.clip(l_hsl[blue_mask] + blue_lum_shift, 0.0, 1.0)

    # ---- Step 8b: Optional Green channel boost (Fuji Green / C200 signature) ----
    if abs(green_sat_boost - 1.0) > 0.001 or abs(green_hue_shift) > 0.001 or abs(green_lum_shift) > 0.001:
        green_mask = (h >= 85.0) & (h <= 155.0)
        if np.any(green_mask):
            s[green_mask] = s[green_mask] * green_sat_boost
            h[green_mask] = h[green_mask] + green_hue_shift
            l_hsl[green_mask] = np.clip(l_hsl[green_mask] + green_lum_shift, 0.0, 1.0)

    # ---- Convert back to RGB ----
    r, g, b = hsl_to_rgb(h, s, l_hsl)
    rgb = np.stack([r, g, b], axis=1)
    rgb = np.clip(rgb, 0.0, None)

    if len(shape) == 1:
        rgb = rgb[0]
    return rgb


# ============================================================================
# Display Gamma
# ============================================================================

DISPLAY_GAMMA = 2.4  # Rec.709 / BT.1886 OETF


def linear_to_display(linear_rgb):
    """Scene-linear → display gamma (sRGB piecewise with 2.4-power tail)."""
    linear = np.asarray(linear_rgb, dtype=np.float64)
    threshold = 0.0031308
    linear_part = 12.92 * linear
    gamma_part = 1.055 * (linear ** (1.0 / DISPLAY_GAMMA)) - 0.055
    return np.where(linear <= threshold, linear_part, gamma_part)


def display_to_linear(display_rgb):
    """Inverse of linear_to_display. Display gamma → scene-linear."""
    d = np.asarray(display_rgb, dtype=np.float64)
    threshold = 0.04045
    linear_part = d / 12.92
    gamma_part = ((d + 0.055) / 1.055) ** DISPLAY_GAMMA
    return np.where(d <= threshold, linear_part, gamma_part)
