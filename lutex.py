#!/usr/bin/env python3
"""
Film Emulation LUT Generator — CLI Entry Point

Usage:
  python lutex.py --list                                          # List available presets
  python lutex.py --preset 5207                                   # Generate .cube LUTs
  python lutex.py --preset 5207 --size 65                         # Custom LUT size
  python lutex.py --apply-cube luts/Kodak_5207.cube pic.jpg       # Apply LUT to a photo
"""

import os
import sys
import argparse

from engine.preset import load_preset, list_presets
from engine.lut3d import generate_vlog_lut, generate_standard_lut, write_cube_file, DEFAULT_LUT_SIZE
from engine.apply import apply_cube_file
from engine.core import M_VGAMUT_TO_REC709


def main():
    parser = argparse.ArgumentParser(
        description='Film Emulation LUT Generator for Panasonic S9'
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preset', type=str, default=None,
                      help='Preset name (e.g. 5207, gold200) — generate .cube LUTs')
    mode.add_argument('--apply-cube', nargs=2, metavar=('CUBE', 'IMAGE'), default=None,
                      help='Apply a .cube LUT to an image (output → output/)')
    mode.add_argument('--list', action='store_true',
                      help='List available presets')

    parser.add_argument('--size', type=int, default=DEFAULT_LUT_SIZE,
                        help=f'LUT grid size (default: {DEFAULT_LUT_SIZE}, must be odd)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output directory for .cube files (generate mode)')
    parser.add_argument('--apply-output', type=str, default=None,
                        help='Output path for applied image (apply mode)')

    args = parser.parse_args()

    # --list mode
    if args.list:
        names = list_presets()
        if not names:
            print("No presets found in presets/ directory.")
        else:
            print("Available presets:")
            for n in names:
                try:
                    p = load_preset(n)
                    print(f"  {n:<16} — {p['title']}")
                except Exception as e:
                    print(f"  {n:<16} — (error: {e})")
        return

    # --apply-cube mode
    if args.apply_cube:
        cube_path, image_path = args.apply_cube
        if not os.path.exists(cube_path):
            print(f"Error: LUT file not found: {cube_path}")
            sys.exit(1)
        if not os.path.exists(image_path):
            print(f"Error: image file not found: {image_path}")
            sys.exit(1)

        project_root = os.path.dirname(os.path.abspath(__file__))
        apply_dir = os.path.join(project_root, 'output')
        os.makedirs(apply_dir, exist_ok=True)

        if args.apply_output:
            out_path = args.apply_output
        else:
            img_base, img_ext = os.path.splitext(os.path.basename(image_path))
            cube_base = os.path.splitext(os.path.basename(cube_path))[0]
            out_path = os.path.join(apply_dir, f"{img_base}_{cube_base}{img_ext or '.jpg'}")

        apply_cube_file(cube_path, image_path, out_path)
        return

    # ---- Generate mode (--preset) ----
    try:
        preset = load_preset(args.preset)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    preset_name = preset['name']
    preset_title = preset['title']
    size = args.size
    assert size >= 2 and size % 2 == 1, "LUT size must be an odd number >= 3"

    project_root = os.path.dirname(os.path.abspath(__file__))
    luts_dir = args.output or os.path.join(project_root, 'luts')
    os.makedirs(luts_dir, exist_ok=True)

    print("=" * 60)
    print(f"Film Emulation LUT Generator")
    print(f"Preset: {preset_name} — {preset_title}")
    print(f"Grid size: {size}³")
    print(f"Output: {luts_dir}")
    print("=" * 60)

    print(f"\nV-Gamut → Rec.709 conversion matrix:")
    for row in M_VGAMUT_TO_REC709:
        print(f"  [{row[0]:+.6f}  {row[1]:+.6f}  {row[2]:+.6f}]")

    t = preset['tone']
    c = preset['color']
    pc = t['per_channel_contrast']
    print(f"\nTone Parameters:")
    print(f"  Black lift:         {t['black_lift']:.5f}")
    print(f"  Shadow toe:         pivot={t['shadow_toe_pivot']:.2f}, power={t['shadow_toe_power']:.2f}")
    print(f"  Contrast:           base={t['contrast']:.2f}, per-channel R={t['contrast']*pc[0]:.3f} G={t['contrast']*pc[1]:.3f} B={t['contrast']*pc[2]:.3f}")
    print(f"  Highlight shoulder: start={t['highlight_shoulder_start']:.2f}, power={t['highlight_shoulder_power']:.2f}")
    print(f"\nColor Parameters:")
    print(f"  Saturation:         global={c['global_saturation']:.2f}, highlight_desat_max={c['highlight_desat_max']:.2f}")
    print(f"  Skin tone:          hue={c['skin_hue_min']:.0f}-{c['skin_hue_max']:.0f}°, sat_adj={c['skin_sat_adjust']:.2f}")
    print(f"  Shadow tint:        [{c['shadow_tint'][0]:.2f}, {c['shadow_tint'][1]:.2f}, {c['shadow_tint'][2]:.2f}]")
    print(f"  Highlight tint:     [{c['highlight_tint'][0]:.2f}, {c['highlight_tint'][1]:.2f}, {c['highlight_tint'][2]:.2f}]")
    if c.get('white_balance_shift_k', 0) != 0:
        print(f"  White balance:      {int(c['white_balance_shift_k']):+d}K")
    if c.get('blue_saturation_boost', 1.0) != 1.0:
        print(f"  Blue boost:         sat={c['blue_saturation_boost']:.2f}, lum={c.get('blue_luminance_shift', 0):+.2f}, hue={c.get('blue_hue_shift', 0):+.0f}°")

    # Generate V-Log LUT (skip if preset doesn't need V-Log)
    skip_vlog = preset.get('skip_vlog', False)
    skip_std = preset.get('skip_standard', False)
    lut_name = preset['lut_name']
    # When both V-Log and Standard LUTs ship, V-Log gets a _VL suffix to
    # distinguish the two files; single-LUT presets use the bare name.
    both = not skip_vlog and not skip_std
    vlog_path = None
    std_path = None

    step = 0
    total_steps = (0 if skip_vlog else 1) + (0 if skip_std else 1)

    if not skip_vlog:
        step += 1
        print(f"\n[{step}/{total_steps}] Generating V-Log → {preset_name.upper()} LUT...")
        vlog_lut = generate_vlog_lut(size, preset)
        vlog_fname = f'{lut_name}_VL.cube' if both else f'{lut_name}.cube'
        vlog_path = os.path.join(luts_dir, vlog_fname)
        write_cube_file(vlog_path, vlog_lut, f"Panasonic S9 V-Log to {preset_title}", photo_style="VLOG")

    # Generate Standard LUT
    if not skip_std:
        step += 1
        print(f"\n[{step}/{total_steps}] Generating Standard → {preset_name.upper()} LUT...")
        std_lut = generate_standard_lut(size, preset)
        std_path = os.path.join(luts_dir, f'{lut_name}.cube')
        write_cube_file(std_path, std_lut, f"Panasonic S9 Standard to {preset_title}", photo_style="STD")

    print(f"\n{'=' * 60}")
    print("Done! Copy .cube files to your S9's SD card:")
    if vlog_path:
        print(f"  {vlog_path}")
    if std_path:
        print(f"  {std_path}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
