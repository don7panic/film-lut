import os
from pathlib import Path
import tempfile
import unittest
import warnings

import numpy as np

from engine.core import apply_tone_curve, linear_to_vlog, vlog_to_linear
from engine.lut3d import apply_lut_to_image, load_cube_file, write_cube_file
from engine.preset import list_presets, load_preset


class VLogFormulaTests(unittest.TestCase):
    def test_linear_to_vlog_matches_panasonic_reference_points(self):
        self.assertAlmostEqual(float(linear_to_vlog(0.0)), 128 / 1023, delta=0.001)
        self.assertAlmostEqual(float(linear_to_vlog(0.01)), 185.1626816065981 / 1023, delta=0.001)
        self.assertAlmostEqual(float(linear_to_vlog(0.18)), 433.04761208161926 / 1023, delta=0.001)
        self.assertAlmostEqual(float(linear_to_vlog(0.9)), 601.6952892319898 / 1023, delta=0.001)

    def test_vlog_to_linear_matches_panasonic_reference_points(self):
        self.assertAlmostEqual(float(vlog_to_linear(128 / 1023)), 0.0, delta=0.001)
        self.assertAlmostEqual(float(vlog_to_linear(185 / 1023)), 0.01, delta=0.001)
        self.assertAlmostEqual(float(vlog_to_linear(433 / 1023)), 0.18, delta=0.001)
        self.assertAlmostEqual(float(vlog_to_linear(602 / 1023)), 0.9, delta=0.005)


class ToneCurveTests(unittest.TestCase):
    def test_apply_tone_curve_handles_black_without_runtime_warning(self):
        params = {
            "tone": {
                "black_lift": 0.0,
                "shadow_toe_pivot": 0.1,
                "shadow_toe_power": 1.0,
                "contrast": 1.0,
                "per_channel_contrast": [1.0, 1.0, 1.0],
                "highlight_shoulder_start": 0.7,
                "highlight_shoulder_power": 1.0,
            }
        }

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = apply_tone_curve(np.zeros((1, 3), dtype=np.float64), params)

        self.assertEqual(caught, [])
        np.testing.assert_allclose(result, [[0.0, 0.0, 0.0]])


class CubeOrderTests(unittest.TestCase):
    def test_write_cube_file_can_include_lumix_photo_style_tag(self):
        lut = np.zeros((2, 2, 2, 3), dtype=np.float64)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "identity.cube")
            write_cube_file(path, lut, "identity", photo_style="VLOG")
            lines = Path(path).read_text().splitlines()

        self.assertEqual(lines[0], 'TITLE "identity"')
        self.assertEqual(lines[1], "#LUMIXPHOTOSTYLE VLOG")

    def test_write_cube_file_uses_red_fastest_order(self):
        lut = np.zeros((2, 2, 2, 3), dtype=np.float64)
        for r in range(2):
            for g in range(2):
                for b in range(2):
                    lut[r, g, b] = [r, g, b]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "identity.cube")
            write_cube_file(path, lut, "identity")
            with open(path) as f:
                data_lines = [
                    line.strip()
                    for line in f
                    if line.strip()
                    and not line.startswith("#")
                    and not line.startswith("TITLE")
                    and not line.startswith("LUT_3D_SIZE")
                    and not line.startswith("DOMAIN")
                ]

        self.assertEqual(
            data_lines,
            [
                "0.00000000 0.00000000 0.00000000",
                "1.00000000 0.00000000 0.00000000",
                "0.00000000 1.00000000 0.00000000",
                "1.00000000 1.00000000 0.00000000",
                "0.00000000 0.00000000 1.00000000",
                "1.00000000 0.00000000 1.00000000",
                "0.00000000 1.00000000 1.00000000",
                "1.00000000 1.00000000 1.00000000",
            ],
        )

    def test_load_cube_file_reads_red_fastest_order(self):
        content = """TITLE "identity"
LUT_3D_SIZE 2
DOMAIN_MIN 0.0 0.0 0.0
DOMAIN_MAX 1.0 1.0 1.0

0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
1.0 1.0 0.0
0.0 0.0 1.0
1.0 0.0 1.0
0.0 1.0 1.0
1.0 1.0 1.0
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "identity.cube")
            with open(path, "w") as f:
                f.write(content)
            lut = load_cube_file(path)

        np.testing.assert_allclose(lut[1, 0, 0], [1.0, 0.0, 0.0])
        np.testing.assert_allclose(lut[0, 1, 0], [0.0, 1.0, 0.0])
        np.testing.assert_allclose(lut[0, 0, 1], [0.0, 0.0, 1.0])


class ShippedLutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parents[1]
        cls.luts_dir = cls.project_root / "luts"

    def test_shipped_luts_match_preset_skip_flags_and_lumix_tags(self):
        for preset_name in list_presets():
            preset = load_preset(preset_name)
            lut_name = preset['lut_name']
            skip_vlog = preset.get("skip_vlog", False)
            skip_std = preset.get("skip_standard", False)
            both = not skip_vlog and not skip_std

            # Standard LUT (or sole LUT): <lut_name>.cube
            std_path = self.luts_dir / f"{lut_name}.cube"
            if skip_std and both:
                self.assertFalse(std_path.exists(), f"{std_path.name} should not ship")
            else:
                tag = "STD" if skip_vlog else ("STD" if both else "VLOG")
                self.assert_lut_has_photo_style_tag(std_path, tag)

            # V-Log LUT when both ship: <lut_name>_VL.cube (distinct name)
            if both:
                vlog_path = self.luts_dir / f"{lut_name}_VL.cube"
                self.assert_lut_has_photo_style_tag(vlog_path, "VLOG")

    def test_shipped_vlog_luts_keep_middle_gray_visible(self):
        mid_gray = np.array([433 / 1023, 433 / 1023, 433 / 1023], dtype=np.float64)

        for preset_name in list_presets():
            preset = load_preset(preset_name)
            if preset.get("skip_vlog", False):
                continue

            lut_name = preset['lut_name']
            both = not preset.get("skip_vlog", False) and not preset.get("skip_standard", False)
            vlog_fname = f"{lut_name}_VL.cube" if both else f"{lut_name}.cube"
            path = self.luts_dir / vlog_fname
            lut = load_cube_file(path)
            output = apply_lut_to_image(lut, mid_gray.reshape(1, 1, 3))[0, 0]
            luma = float(output @ np.array([0.2126, 0.7152, 0.0722]))

            self.assertGreater(luma, 0.2, f"{path.name} maps V-Log middle gray too dark")

    def assert_lut_has_photo_style_tag(self, path, tag):
        self.assertTrue(path.exists(), f"{path.name} should ship")
        lines = path.read_text().splitlines()
        self.assertGreaterEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith("TITLE "), f"{path.name} should start with TITLE")
        self.assertEqual(lines[1], f"#LUMIXPHOTOSTYLE {tag}")


if __name__ == "__main__":
    unittest.main()
