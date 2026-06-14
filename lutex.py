#!/usr/bin/env python3
"""
Film Emulation LUT Generator — CLI Entry Point

Usage:
  python lutex.py --list                        # List available presets
  python lutex.py --preset 5219                  # Generate .cube LUTs
  python lutex.py --preset hassy_blue --preview  # Generate + test image
  python lutex.py --preset 5219 --apply pic.jpg  # Preview on a photo
  python lutex.py --preset hassy_blue --size 65  # Custom LUT size
"""

import os
import sys
import argparse

from engine.preset import load_preset, list_presets
from engine.lut3d import generate_vlog_lut, generate_standard_lut, write_cube_file, DEFAULT_LUT_SIZE
from engine.apply import apply_lut_to_file, generate_test_image
from engine.core import M_VGAMUT_TO_REC709


def main():
    parser = argparse.ArgumentParser(
        description='Film Emulation LUT Generator for Panasonic S9'
    )
    parser.add_argument('--preset', type=str, default=None,
                        help='Preset name (e.g. 5219, hassy_blue)')
    parser.add_argument('--list', action='store_true',
                        help='List available presets')
    parser.add_argument('--size', type=int, default=DEFAULT_LUT_SIZE,
                        help=f'LUT grid size (default: {DEFAULT_LUT_SIZE}, must be odd)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output directory for .cube files')
    parser.add_argument('--preview', action='store_true',
                        help='Generate test reference image')
    parser.add_argument('--apply', type=str, default=None, metavar='IMAGE',
                        help='Apply LUT to an image and save result')
    parser.add_argument('--apply-type', type=str, default='standard',
                        choices=['standard', 'vlog'],
                        help='Input type for --apply')
    parser.add_argument('--apply-output', type=str, default=None,
                        help='Output path for --apply')
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

    # Require --preset for all other modes
    if not args.preset:
        parser.error("--preset is required (use --list to see available presets)")

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
    apply_dir = os.path.join(project_root, 'output')
    os.makedirs(luts_dir, exist_ok=True)
    os.makedirs(apply_dir, exist_ok=True)

    # --apply mode
    if args.apply:
        input_path = args.apply
        if not os.path.exists(input_path):
            print(f"Error: file not found: {input_path}")
            sys.exit(1)
        if args.apply_output:
            out_path = args.apply_output
        else:
            base, ext = os.path.splitext(os.path.basename(input_path))
            out_path = os.path.join(apply_dir, f"{base}_{preset_name}{ext}")
        apply_lut_to_file(input_path, out_path, args.apply_type, preset, size)
        return

    # ---- Generation mode ----
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
    vlog_path = None
    std_path = None

    step = 0
    total_steps = (0 if skip_vlog else 1) + (0 if skip_std else 1)

    if not skip_vlog:
        step += 1
        print(f"\n[{step}/{total_steps}] Generating V-Log → {preset_name.upper()} LUT...")
        vlog_lut = generate_vlog_lut(size, preset)
        vlog_path = os.path.join(luts_dir, f'S9_VLog_to_{preset_name}.cube')
        write_cube_file(vlog_path, vlog_lut, f"Panasonic S9 V-Log to {preset_title}")

    # Generate Standard LUT
    if not skip_std:
        step += 1
        print(f"\n[{step}/{total_steps}] Generating Standard → {preset_name.upper()} LUT...")
        std_lut = generate_standard_lut(size, preset)
        std_path = os.path.join(luts_dir, f'S9_Standard_to_{preset_name}.cube')
        write_cube_file(std_path, std_lut, f"Panasonic S9 Standard to {preset_title}")

    # Preview
    if args.preview:
        generate_test_image(preset)

    print(f"\n{'=' * 60}")
    print("Done! Copy .cube files to your S9's SD card:")
    if vlog_path:
        print(f"  {vlog_path}")
    if std_path:
        print(f"  {std_path}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
