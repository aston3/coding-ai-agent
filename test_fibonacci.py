import unittest
from fibonacci import generate_fibonacci

class TestFibonacciGenerator(unittest.TestCase):
    def test_zero_length(self):
        self.assertEqual(generate_fibonacci(0), [])
        
    def test_one_length(self):
        self.assertEqual(generate_fibonacci(1), [0])
        
    def test_two_length(self):
        self.assertEqual(generate_fibonacci(2), [0, 1])
        
    def test_five_length(self):
        self.assertEqual(generate_fibonacci(5), [0, 1, 1, 2, 3])
        
    def test_ten_length(self):
        self.assertEqual(generate_fibonacci(10), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])

if __name__ == '__main__':
    unittest.main()