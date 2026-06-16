import os
import tempfile
import unittest

import numpy as np

from engine.core import linear_to_vlog, vlog_to_linear
from engine.lut3d import load_cube_file, write_cube_file


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


class CubeOrderTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
