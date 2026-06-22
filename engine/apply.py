"""
Film LUT Engine — Image Application
=====================================
Read a .cube LUT, apply it to an image via trilinear interpolation,
and save the result.
"""

import numpy as np

from .lut3d import load_cube_file, apply_lut_to_image


def apply_cube_file(cube_path, image_path, output_path):
    """Read a .cube LUT, apply it to an image, and save the result.

    The .cube is treated as a complete color transform — input pixels are
    fed directly into the LUT without any pre-decode (no V-Log / gamma
    interpretation), because the .cube already encodes the full pipeline.

    Args:
        cube_path:   Path to the source .cube file.
        image_path:  Path to the source image (JPG, PNG, …).
        output_path: Path for the result image.
    """
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("⚠ Pillow not installed. Install with: pip install Pillow")
        return

    print(f"Loading LUT:  {cube_path}")
    lut = load_cube_file(cube_path)
    print(f"  Grid: {lut.shape[0]}³")

    print(f"Loading image: {image_path}")
    img = Image.open(image_path).convert('RGB')
    img = ImageOps.exif_transpose(img)
    print(f"  Size: {img.size[0]}x{img.size[1]}")

    pixels = np.array(img, dtype=np.float64) / 255.0

    print(f"  Applying LUT...")
    result = apply_lut_to_image(lut, pixels)
    result_uint8 = (result * 255.0).clip(0, 255).astype(np.uint8)

    out_img = Image.fromarray(result_uint8, 'RGB')
    out_img.save(output_path, quality=95)
    print(f"  ✓ {output_path} — {out_img.size[0]}x{out_img.size[1]}")
