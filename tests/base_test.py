import os, sys
mod_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, mod_path)
import autosar
import xml.etree.ElementTree as ElementTree
import unittest

class TestBase(unittest.TestCase):

   # def test_filter_packages(self):
   #    result = autosar.base.filter_package_refs(['/A', '/B', '/C'], ['/A', '/B', '/D'])
   #    self.assertEqual(result, ['/A', '/B'])
   # 
   #    result = autosar.base.filter_package_refs(['/A'], ['/A/X', '/A/Q', '/A/P'])
   #    self.assertEqual(result, ['/A'])
   # 
   #    result = autosar.base.filter_package_refs(['/A/X', '/A/Q'], ['/A/X', '/A/Q', '/A/P'])
   #    self.assertEqual(result, ['/A/X', '/A/Q'])
   
   def test_filter(self):
      ws = autosar.workspace()
      p1 = ws.createPackage('Package1')
      p2 = ws.createPackage('Package2')
      pc1 = p1.createSubPackage('Child1')
      pc2 = p1.createSubPackage('Child2')
      A = autosar.element.Element('A'); p1.append(A)
      B = autosar.element.Element('B'); p1.append(B)
      C = autosar.element.Element('C'); pc1.append(C)
      D = autosar.element.Element('D'); pc1.append(D)
      E = autosar.element.Element('E'); p2.append(E)
      F = autosar.element.Element('F'); p2.append(F)
      G = autosar.element.Element('G'); p2.append(G)
      self.assertEqual(A.ref, '/Package1/A')
      self.assertEqual(B.ref, '/Package1/B')
      self.assertEqual(C.ref, '/Package1/Child1/C')
      self.assertEqual(D.ref, '/Package1/Child1/D')
      self.assertEqual(E.ref, '/Package2/E')
      self.assertEqual(F.ref, '/Package2/F')
      self.assertEqual(G.ref, '/Package2/G')
      self.assertTrue(autosar.base.applyFilter(A.ref, [['Package1']]))
      self.assertFalse(autosar.base.applyFilter(A.ref, [['Package1', 'Child1']]))
      self.assertTrue(autosar.base.applyFilter(C.ref, [['Package1', 'Child1']]))
      self.assertTrue(autosar.base.applyFilter(D.ref, [['Package1', 'Child1', 'D']]))
      self.assertFalse(autosar.base.applyFilter(C.ref, [['Package1', 'Child1', 'D']]))      
      self.assertFalse(autosar.base.applyFilter(E.ref, [['Package1']]))
      self.assertTrue(autosar.base.applyFilter(E.ref, [['Package2']]))
      self.assertTrue(autosar.base.applyFilter(A.ref, [['Package1', '*']]))
      self.assertTrue(autosar.base.applyFilter(C.ref, [['Package1', '*']]))
      self.assertTrue(autosar.base.applyFilter(C.ref, [['Package1']]))
      self.assertTrue(autosar.base.applyFilter('Package1', [['Package1', 'Child1', 'D']]))
      self.assertTrue(autosar.base.applyFilter('Package1/Child1', [['Package1', 'Child1', 'D']]))
      self.assertTrue(autosar.base.applyFilter('Package1/Child1/D', [['Package1', 'Child1', 'D']]))
      self.assertFalse(autosar.base.applyFilter('Package1/Child/C', [['Package1', 'Child1', 'D']]))
      
      
   def test_prepare_filters(self):
      self.assertEqual(['Package1'], autosar.base.prepareFilter('/Package1'))
      self.assertEqual(['Package1', 'Child1'], autosar.base.prepareFilter('/Package1/Child1'))
      self.assertEqual(['Package1', 'Child1', '*'], autosar.base.prepareFilter('/Package1/Child1/'))
      self.assertEqual(['Package1', 'Child1', '*'], autosar.base.prepareFilter('/Package1/Child1/*'))
      

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