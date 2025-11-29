import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_all_tests():
    """Функция для поиска всех unittest-тестов и их запуска"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests/', pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    run_all_tests()
