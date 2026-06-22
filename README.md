# Film LUT Engine

Film emulation 3D LUT generator for the Panasonic S9 camera. Generates `.cube` LUT files that emulate classic film stocks using parameterized color science.

## Presets

| Preset | Description |
|--------|-------------|
| `5207` | Kodak Vision3 250D (5207) — natural soft skin tones, clear blue skies, neutral daylight balance |
| `5219` | Kodak Vision3 5219 (500T) — warm skin tones, cyan-biased shadows, 3-layer emulsion contrast |
| `gold200` | Kodak Gold 200 — warm golden consumer film, amber reds, nostalgic skies |
| `hassy_blue` | Hasselblad HNCS-inspired — natural color with enhanced blue rendering |
| `ricoh_positive_film` | Ricoh Positive Film (ポジフィルム調) — Japanese positive film look |
| `c200` | Fujifilm Fujicolor C200 (Japan) — vintage documentary, soft cinematic shadows, warm-red shadow signature |

## Quick Start

```bash
# With uv (recommended)
uv run python lutex.py --list

# Or with pip
pip install -e .
python lutex.py --list
```

## CLI Reference

```bash
# List all available presets
uv run python lutex.py --list

# Generate .cube LUTs (output → luts/)
uv run python lutex.py --preset 5219
uv run python lutex.py --preset gold200 --size 65
uv run python lutex.py --preset 5219 --output /path/to/luts

# Apply a .cube LUT to a photo (output → output/)
uv run python lutex.py --apply-cube luts/Ricoh_positive.cube samples/vlog.jpg
uv run python lutex.py --apply-cube luts/Ricoh_positive.cube samples/vlog.jpg --apply-output result.jpg
```

## Project Structure

```
film/
├── engine/           # Core library
│   ├── core.py       #   V-Log, gamut conversion, tone curves, HSL, color grade
│   ├── apply.py      #   Image loading, LUT application, test image generation
│   ├── lut3d.py      #   3D LUT generation, .cube read/write, trilinear interpolation
│   └── preset.py     #   Preset loader & validation
├── presets/          # Film preset definitions (parameter dicts)
├── tools/            # Analysis & debugging scripts
├── docs/             # Research notes & design specs
├── samples/          # Sample photos for testing
├── luts/             # Generated .cube LUT files (tracked in git)
├── output/           # Test images, applied photos (gitignored)
└── lutex.py          # CLI entry point
```

## Using on Panasonic S9

1. Generate the LUTs you want: `uv run python lutex.py --preset 5219`
2. Copy the `.cube` files from `luts/` to your S9's SD card:
   - `S9_VLog_to_*.cube` — for V-Log shooting
   - `S9_Standard_to_*.cube` — for Standard (Rec.709) shooting
3. Load them via the S9's Real-Time LUT function

## Dependencies

- Python ≥ 3.10
- NumPy ≥ 1.24
- Pillow ≥ 9.0
