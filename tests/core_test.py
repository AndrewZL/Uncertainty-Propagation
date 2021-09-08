import unittest
from propagate_uncertainty import *


class TestRounding(unittest.TestCase):
    def test_negative(self):
        self.assertEqual(round_uncertainty(0.123, 0.02), (0.12, 0.02, 2))

    def test_larger_one(self):
        self.assertEqual(round_uncertainty(123, 10), (120, 10, -1))

    def test_larger_one_ten(self):
        self.assertEqual(round_uncertainty(200, 12), (200, 10, -1))

    def test_effective_0(self):
        self.assertEqual(round_uncertainty(10, 254), (0, 300, -2))

    def test_roundup(self):
        self.assertEqual(round_uncertainty(0.098, 0.099), (0.1, 0.1, 1))


class TestPropagation(unittest.TestCase):
    def test_addition_simple(self):
        self.assertEqual(propagate_error('a - b', 'a,b', [[2, 0.03], [0.88, 0.04]]), (1.12, 0.05))

    def test_addition_multiple(self):
        x, u = propagate_error('a + b + (c + (d))', 'a, b, c, d', [[2, 3], [1, 0.5], [42.42, 0.1], [19.3333, 6]])
        self.assertAlmostEqual(x, 64.7533)
        self.assertAlmostEqual(u, 6.7276, 4)

    def test_multiplication_simple(self):
        x, u = propagate_error('a * 1/b', 'a, b', [[120, 3], [20, 1.2]])
        self.assertAlmostEqual(x, 6)
        self.assertAlmostEqual(u, 0.39)

    def test_power(self):
        x, u = propagate_error('1/T', 'T', [[0.2, 0.01]])
        self.assertAlmostEqual(x, 5)
        self.assertAlmostEqual(u, 0.25)

    def test_constant(self):
        x, u = propagate_error('1/2 * 9.8 * t^2', 't', [[1.3, 0.2]])
        self.assertAlmostEqual(x, 8.281)
        self.assertAlmostEqual(u, 2.548)

    def test_trig(self):
        x, u = propagate_error('sqrt(R * g * tan(theta))', 'R, g, theta',
                               [[6.85, 0.12], [9.81, 0.1], [0.7504926785, 0.0139626]])
        self.assertAlmostEqual(x, 7.916035309, 4)
        self.assertAlmostEqual(u, 0.136791, 4)
