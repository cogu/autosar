import os, sys
mod_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, mod_path)
import autosar
import xml.etree.ElementTree as ElementTree
import unittest

class TestBase(unittest.TestCase):

   def test_filter_packages(self):
      result = autosar.base.filter_package_refs(['/A', '/B', '/C'], ['/A', '/B', '/D'])
      self.assertEqual(result, ['/A', '/B'])

      result = autosar.base.filter_package_refs(['/A'], ['/A/X', '/A/Q', '/A/P'])
      self.assertEqual(result, ['/A'])

      result = autosar.base.filter_package_refs(['/A/X', '/A/Q'], ['/A/X', '/A/Q', '/A/P'])
      self.assertEqual(result, ['/A/X', '/A/Q'])
         

   def test_parseAutosarVersionAndSchema3(self):
      xmlData="""<?xml version="1.0" encoding="UTF-8"?>
      <AUTOSAR xsi:schemaLocation="http://autosar.org/3.0.2 autosar_302_ext.xsd" xmlns="http://autosar.org/3.0.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      </AUTOSAR>
      """
      xmlRoot = ElementTree.fromstring(xmlData)
      (major, minor, patch, schema) = autosar.base.parseAutosarVersionAndSchema(xmlRoot)
      self.assertEqual(major, 3)
      self.assertEqual(minor, 0)
      self.assertEqual(patch, 2)
      self.assertEqual(schema, 'autosar_302_ext.xsd')
      
      xmlData="""<?xml version="1.0" encoding="UTF-8"?>
      <AUTOSAR xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://autosar.org/3.2.2" xsi:schemaLocation="http://autosar.org/3.2.2 AUTOSAR.xsd">
      </AUTOSAR>"""
      xmlRoot = ElementTree.fromstring(xmlData)
      (major, minor, patch, schema) = autosar.base.parseAutosarVersionAndSchema(xmlRoot)
      self.assertEqual(major, 3)
      self.assertEqual(minor, 2)
      self.assertEqual(patch, 2)
      self.assertEqual(schema, 'AUTOSAR.xsd')
   
   def test_parseAutosarVersionAndSchema4(self):
      xmlData="""<?xml version="1.0" encoding="utf-8"?>
      <AUTOSAR xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-1.xsd" xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      </AUTOSAR>
      """
      xmlRoot = ElementTree.fromstring(xmlData)
      (major, minor, patch, schema) = autosar.base.parseAutosarVersionAndSchema(xmlRoot)
      self.assertEqual(major, 4)
      self.assertEqual(minor, 2)
      self.assertEqual(patch, 1)
      self.assertEqual(schema, 'AUTOSAR_4-2-1.xsd')

      xmlData="""<?xml version="1.0" encoding="utf-8"?>
      <AUTOSAR xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2.xsd" xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      </AUTOSAR>
      """      
      xmlRoot = ElementTree.fromstring(xmlData)
      (major, minor, patch, schema) = autosar.base.parseAutosarVersionAndSchema(xmlRoot)
      self.assertEqual(major, 4)
      self.assertEqual(minor, 2)
      self.assertEqual(patch, 2)
      self.assertEqual(schema, 'AUTOSAR_4-2-2.xsd')

if __name__ == '__main__':
    unittest.main()