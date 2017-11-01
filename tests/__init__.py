import unittest

def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('.', pattern='*_test.py')
    return test_suite