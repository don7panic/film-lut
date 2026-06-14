# LUT Engine Refactor + Hasselblad Blue Preset

**Date:** 2026-06-13
**Status:** Design

## Overview

Refactor `5219.py` into a shared LUT engine with pluggable presets, and add a **Hasselblad Blue** film emulation preset. The engine handles all color science and LUT generation; presets are self-contained parameter files.

## Motivation

Multiple LUTs are planned (5219, Hasselblad Blue, and more). A shared engine avoids duplicating V-Log math, gamut conversion, tone curve logic, and .cube I/O across scripts.

## File Structure

```
film/
├── lutex.py              # CLI entry point (replaces 5219.py)
├── engine/
│   ├── __init__.py
│   ├── core.py           # V-Log math, gamut conversion, tone curve, color grade
│   ├── lut3d.py          # 3D LUT generation, .cube read/write
│   ├── apply.py          # Apply LUT to images (trilinear interpolation)
│   └── preset.py         # Preset loader, validation, registration
└── presets/
    ├── __init__.py
    ├── 5219.py           # Kodak 5219 parameters
    └── hassy_blue.py     # Hasselblad Blue parameters
```

## CLI Interface

```bash
# Generate .cube LUTs for a preset
uv run python lutex.py --preset 5219
uv run python lutex.py --preset hassy-blue

# Apply LUT to an image (preview)
uv run python lutex.py --preset 5219 --apply photo.jpg
uv run python lutex.py --preset hassy-blue --apply photo.jpg --apply-type vlog

# Generate test reference image
uv run python lutex.py --preset 5219 --preview

# List available presets
uv run python lutex.py --list

# Global options
uv run python lutex.py --preset 5219 --size 65 --output ./my_luts/
```

## Engine Module Design

### `engine/core.py`
- `vlog_to_linear(v)` — V-Log inverse
- `linear_to_vlog(x)` — forward V-Log (validation)
- `vgamut_to_rec709(rgb)` — gamut matrix conversion
- `apply_tone_curve(linear_rgb, params)` — S-curve with per-channel contrast
- `apply_color_grade(linear_rgb, params)` — HSL-based creative adjustments
- `linear_to_display(linear_rgb)` — scene-linear → Rec.709 gamma (2.4)

All parameterized functions accept a `params` dict (from the preset).

### `engine/lut3d.py`
- `generate_vlog_lut(size, params)` — V-Log/V-Gamut → preset → Rec.709
- `generate_standard_lut(size, params)` — Rec.709 → preset → Rec.709
- `generate_3dlut_grid(size)` — meshgrid helper
- `write_cube_file(path, lut_data, title)`
- `apply_lut_to_image(lut_data, image)` — trilinear interpolation

### `engine/apply.py`
- `apply_lut_to_file(input_path, output_path, lut_type, params)` — load image, apply LUT, save
- EXIF orientation handling (ImageOps.exif_transpose)

### `engine/preset.py`
- `load_preset(name)` — import and validate preset module
- `list_presets()` — scan presets/ directory
- `validate_preset(data)` — check required keys, types, ranges

## Preset Format

Each preset is a Python module exporting a `PRESET` dict:

```python
PRESET = {
    'name': 'hassy-blue',
    'title': 'Hasselblad Blue (Medium Format)',
    'tone': {
        'black_lift': 0.0010,
        'shadow_toe_pivot': 0.12,
        'shadow_toe_power': 0.85,
        'contrast': 0.92,
        'highlight_shoulder_start': 0.74,
        'highlight_shoulder_power': 1.18,
        'per_channel_contrast': [1.00, 1.00, 1.00],
    },
    'color': {
        'shadow_tint': [1.00, 1.00, 1.02],
        'highlight_tint': [1.00, 1.00, 1.01],
        'global_saturation': 0.95,
        'highlight_desat_start': 0.65,
        'highlight_desat_max': 0.08,
        'skin_hue_min': 10.0,
        'skin_hue_max': 35.0,
        'skin_sat_adjust': 0.92,
        'teal_push': 0.0,
        'orange_push': 0.0,
        # Hasselblad Blue specific
        'blue_saturation_boost': 1.12,
        'blue_luminance_shift': -0.03,
        'blue_hue_shift': 3.0,
        'white_balance_shift_k': -250,
    },
}
```

## Hasselblad Blue Preset Characteristics

- **Blue channel:** +12% saturation, -3% luminance (deeper), +3° hue toward cyan
- **White balance:** -250K (slightly cool)
- **Contrast:** 0.92 (medium format smooth tonal transitions)
- **Saturation:** 0.95 (slightly desaturated overall, blues compensated)
- **Skin protection:** warm compensation to offset cool bias
- **Greens:** slightly desaturated (doesn't compete with blues)
- **No teal/orange push:** keeps the clean, natural look

## 5219 Preset Migration

The existing `5219.py` parameters are migrated to `presets/5219.py` with the exact same values currently in use (research-calibrated v2).

## Dependencies

- Python 3.9+
- NumPy (color math, LUT generation)
- Pillow (image loading/saving, optional for --apply and --preview)

## Backward Compatibility

- `5219.py` is removed; users run `lutex.py --preset 5219` instead
- Generated .cube files have identical output for 5219 preset
