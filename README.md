# Film LUT Engine

Film emulation 3D LUT generator for the Panasonic S9 camera. Generates `.cube` LUT files that emulate classic film stocks using parameterized color science.

## Presets

| Preset | Description |
|--------|-------------|
| `5219` | Kodak Vision3 5219 (500T) — warm skin, cyan shadows, 3-layer contrast |
| `gold200` | Kodak Gold 200 — warm golden consumer film |
| `hassy_blue` | Hasselblad HNCS-inspired blue rendering |
| `ricoh_positive_film` | Ricoh Positive Film emulation |

## Quick Start

```bash
# Install dependencies
pip install -e .

# List available presets
python lutex.py --list

# Generate .cube LUTs
python lutex.py --preset 5219
python lutex.py --preset gold200 --preview

# Apply a LUT to a photo
python lutex.py --preset 5219 --apply samples/Z30_3923.JPG
```

Outputs go to `output/` by default.

## Project Structure

```
film/
├── engine/           # Core library (color science, LUT generation, image I/O)
│   ├── core.py       #   V-Log, gamut conversion, tone curves, HSL, color grade
│   ├── apply.py      #   Image loading, LUT application, test image generation
│   ├── lut3d.py      #   3D LUT generation, .cube read/write, trilinear interpolation
│   └── preset.py     #   Preset loader & validation
├── presets/          # Film preset definitions (parameter dicts)
├── tools/            # Analysis & debugging scripts
├── docs/             # Research notes & design specs
├── luts/             # Generated .cube LUT files (tracked)
├── output/           # Test images, comparisons, applied photos (gitignored)
└── lutex.py          # CLI entry point
```

## Dependencies

- Python ≥ 3.10
- NumPy ≥ 1.24
- Pillow ≥ 9.0
