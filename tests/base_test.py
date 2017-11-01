import os, sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import autosar

class TestAutosarBase(unittest.TestCase):

   def test_filter_packages(self):
      result = autosar.base.filter_package_refs(['/A', '/B', '/C'], ['/A', '/B', '/D'])
      self.assertEqual(result, ['/A', '/B'])

      result = autosar.base.filter_package_refs(['/A'], ['/A/X', '/A/Q', '/A/P'])
      self.assertEqual(result, ['/A'])

      result = autosar.base.filter_package_refs(['/A/X', '/A/Q'], ['/A/X', '/A/Q', '/A/P'])
      self.assertEqual(result, ['/A/X', '/A/Q'])
         
if __name__ == '__main__':
    unittest.main()