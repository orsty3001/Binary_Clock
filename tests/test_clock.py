import datetime as dt
import unittest
import cairo
from binary_watch import time_bits, draw_clock


class ClockTests(unittest.TestCase):
    def test_reference_example(self):
        self.assertEqual(time_bits(18, 42, 13), (
            (False, True, False, False, True, False),
            (True, False, True, False, True, False),
            (False, False, True, True, False, True)))

    def test_full_day(self):
        for seconds in range(86400):
            h, rem = divmod(seconds, 3600)
            m, s = divmod(rem, 60)
            columns = time_bits(h, m, s)
            decoded = tuple(sum(2 ** (5-i) for i, on in enumerate(col) if on)
                            for col in columns)
            self.assertEqual(decoded, (h, m, s))
            self.assertFalse(columns[0][0])

    def test_invalid_time(self):
        for values in [(-1, 0, 0), (24, 0, 0), (0, 60, 0), (0, 0, 60)]:
            with self.assertRaises(ValueError):
                time_bits(*values)

    def test_render_sizes_and_controls(self):
        for w, h in [(320, 430), (420, 640), (1920, 1080)]:
            for enabled in (False, True):
                surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
                draw_clock(cairo.Context(surface), w, h,
                           dt.datetime(2026, 1, 1, 23, 59, 59), .2, enabled, enabled)
                surface.flush()
                self.assertTrue(any(surface.get_data()))


if __name__ == '__main__':
    unittest.main()
