"""
Film LUT Engine — Image Application
=====================================
Load images, apply LUTs via trilinear interpolation, save results.
Also generates synthetic test reference images.
"""

import os
import numpy as np

from .core import (
    apply_tone_curve,
    apply_color_grade,
    linear_to_display,
    rgb_to_hsl,
    hsl_to_rgb,
)
from .lut3d import (
    apply_lut_to_image,
    generate_vlog_lut,
    generate_standard_lut,
    DEFAULT_LUT_SIZE,
)


def apply_lut_to_file(input_path, output_path, lut_type, params,
                       lut_size=DEFAULT_LUT_SIZE):
    """Load an image, generate and apply LUT, save result.

    Args:
        input_path:  Path to source image (JPG, PNG, …)
        output_path: Path for result image
        lut_type:    ``'standard'`` (Rec.709 input) or ``'vlog'`` (V-Log input)
        params:      Preset parameter dict
        lut_size:    LUT grid resolution
    """
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("⚠ Pillow not installed. Install with: pip install Pillow")
        return

    print(f"Loading: {input_path}")
    img = Image.open(input_path).convert('RGB')
    img = ImageOps.exif_transpose(img)
    print(f"  Size: {img.size[0]}x{img.size[1]}")

    pixels = np.array(img, dtype=np.float64) / 255.0

    print(f"  Applying {lut_type.upper()} → {params['title']} LUT...")
    if lut_type == 'vlog':
        lut_data = generate_vlog_lut(lut_size, params)
    else:
        lut_data = generate_standard_lut(lut_size, params)

    result = apply_lut_to_image(lut_data, pixels)
    result_uint8 = (result * 255.0).clip(0, 255).astype(np.uint8)

    out_img = Image.fromarray(result_uint8, 'RGB')
    out_img.save(output_path, quality=95)
    print(f"  ✓ {output_path} — {out_img.size[0]}x{out_img.size[1]}")


# ---------------------------------------------------------------------------
# Test reference image generation
# ---------------------------------------------------------------------------

def _test_strip(lut_func, width=1920, height=200):
    """Horizontal ramp: grayscale + R / G / B ramps."""
    x = np.linspace(0, 1, width, dtype=np.float64)
    h_gray = int(height * 0.4)
    h_rgb   = int(height * 0.2)
    h_b     = height - h_gray - 2 * h_rgb

    strips = []
    gray = np.tile(x, (h_gray, 1))
    strips.append(np.stack([gray, gray, gray], axis=-1))
    strips.append(np.stack([x, np.zeros_like(x), np.zeros_like(x)], axis=-1).reshape(1, width, 3).repeat(h_rgb, axis=0))
    strips.append(np.stack([np.zeros_like(x), x, np.zeros_like(x)], axis=-1).reshape(1, width, 3).repeat(h_rgb, axis=0))
    strips.append(np.stack([np.zeros_like(x), np.zeros_like(x), x], axis=-1).reshape(1, width, 3).repeat(h_b, axis=0))

    image = np.concatenate(strips, axis=0)
    flat = image.reshape(-1, 3)
    result = np.clip(lut_func(flat), 0, 1)
    return (result.reshape(image.shape) * 255).astype(np.uint8)


def _hue_wheel(lut_func, radius=300):
    """Hue/saturation wheel with LUT applied."""
    size = radius * 2
    y, x = np.ogrid[-radius:radius, -radius:radius]
    dist = np.sqrt(x*x + y*y) / radius
    hue = ((np.arctan2(y, x) / (2*np.pi)) % 1.0) * 360.0
    sat = np.clip(dist, 0.0, 1.0)
    lum = np.full_like(sat, 0.5)

    r, g, b = hsl_to_rgb(hue.flatten(), sat.flatten(), lum.flatten())
    rgb_flat = np.column_stack([r, g, b])
    result = lut_func(rgb_flat).reshape(size, size, 3)
    result[dist > 1.0] = 0.2
    return (result * 255).astype(np.uint8)


def generate_test_image(params, output_path=None):
    """Generate a before/after test reference image for a preset.

    Saves to ``output_path`` or ``<cwd>/test_reference_<name>.png``.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("⚠ Pillow not installed. Install with: pip install Pillow")
        return

    name = params['name']
    title = params['title']

    print(f"\nGenerating test reference image for '{title}'...")

    # Build pipeline functions
    def preset_pipeline(rgb_linear):
        tonemapped = apply_tone_curve(rgb_linear, params)
        graded = apply_color_grade(tonemapped, params)
        return linear_to_display(graded)

    def neutral_pipeline(rgb_linear):
        return linear_to_display(rgb_linear)

    strip_h, strip_w = 200, 1920
    wheel_r = 300

    before_strip = _test_strip(neutral_pipeline, strip_w, strip_h)
    after_strip  = _test_strip(preset_pipeline, strip_w, strip_h)
    before_wheel = _hue_wheel(neutral_pipeline, wheel_r)
    after_wheel  = _hue_wheel(preset_pipeline, wheel_r)

    gap = 20
    total_h = wheel_r * 2 + 80 + gap * 2
    total_w = strip_w + wheel_r * 4 + gap * 3 + 40

    canvas = np.ones((total_h, total_w, 3), dtype=np.uint8) * 30

    canvas[60:60 + strip_h, 20:20 + strip_w] = before_strip
    canvas[60 + strip_h + gap:60 + strip_h * 2 + gap, 20:20 + strip_w] = after_strip

    wx = 20 + strip_w + gap
    wy = 60
    canvas[wy:wy + wheel_r * 2, wx:wx + wheel_r * 2] = before_wheel
    wx2 = wx + wheel_r * 2 + gap
    canvas[wy:wy + wheel_r * 2, wx2:wx2 + wheel_r * 2] = after_wheel

    img = Image.fromarray(canvas)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()

    draw.text((20, 15), f"{title} — Test Reference", fill=(255, 255, 255), font=font_title)
    draw.text((20, 60), "Before (Linear → sRGB)", fill=(200, 200, 200), font=font_label)
    draw.text((20, 60 + strip_h + gap), f"After (Linear → {title})", fill=(200, 200, 200), font=font_label)
    draw.text((wx, 60), "Hue Wheel: Before", fill=(200, 200, 200), font=font_label)
    draw.text((wx2, 60), f"Hue Wheel: {name}", fill=(200, 200, 200), font=font_label)

    if output_path is None:
        output_path = f'test_reference_{name}.png'
    img.save(output_path, 'PNG')
    print(f'  ✓ {output_path} — {total_w}x{total_h} pixels')
