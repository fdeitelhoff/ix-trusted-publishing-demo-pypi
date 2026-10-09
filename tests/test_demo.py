import unittest

from tp_demo import add


class AddTests(unittest.TestCase):
    def test_positive_and_negative_numbers(self):
        self.assertEqual(add(7, -3), 4)


if __name__ == "__main__":
    unittest.main()
