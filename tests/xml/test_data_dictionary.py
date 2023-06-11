"""
Unit tests for elements related to data definitions
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402


class TestSwBaseType(unittest.TestCase):
    def test_write_default(self):
        element = ar_element.SwBaseType('Typename')
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
</SW-BASE-TYPE>''')

    def test_read_default(self):
        xml = '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
</SW-BASE-TYPE>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwBaseType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBaseType)
        self.assertEqual(elem.name, 'Typename')

    def test_write_size(self):
        element = ar_element.SwBaseType('Typename', size=16)
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <BASE-TYPE-SIZE>16</BASE-TYPE-SIZE>
</SW-BASE-TYPE>''')

    def test_read_size(self):
        xml = '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <BASE-TYPE-SIZE>16</BASE-TYPE-SIZE>
</SW-BASE-TYPE>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwBaseType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBaseType)
        self.assertEqual(elem.name, 'Typename')
        self.assertEqual(elem.size, 16)

    def test_write_max_size(self):
        element = ar_element.SwBaseType('Typename', max_size=32)
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <MAX-BASE-TYPE-SIZE>32</MAX-BASE-TYPE-SIZE>
</SW-BASE-TYPE>''')

    def test_read_max_size(self):
        xml = '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <MAX-BASE-TYPE-SIZE>32</MAX-BASE-TYPE-SIZE>
</SW-BASE-TYPE>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwBaseType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBaseType)
        self.assertEqual(elem.name, 'Typename')
        self.assertEqual(elem.max_size, 32)

    def test_write_encoding(self):
        element = ar_element.SwBaseType('Typename', encoding='IEEE754')
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <BASE-TYPE-ENCODING>IEEE754</BASE-TYPE-ENCODING>
</SW-BASE-TYPE>''')

    def test_read_encoding(self):
        xml = '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <BASE-TYPE-ENCODING>IEEE754</BASE-TYPE-ENCODING>
</SW-BASE-TYPE>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwBaseType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBaseType)
        self.assertEqual(elem.name, 'Typename')
        self.assertEqual(elem.encoding, 'IEEE754')

    def test_write_alignment(self):
        element = ar_element.SwBaseType('Typename', alignment=512)
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <MEM-ALIGNMENT>512</MEM-ALIGNMENT>
</SW-BASE-TYPE>''')

    def test_read_alignment(self):
        xml = '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <MEM-ALIGNMENT>512</MEM-ALIGNMENT>
</SW-BASE-TYPE>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwBaseType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBaseType)
        self.assertEqual(elem.name, 'Typename')
        self.assertEqual(elem.alignment, 512)

    def test_write_byte_order(self):
        element = ar_element.SwBaseType(
            'Typename', byte_order=ar_enum.ByteOrder.BIG_ENDIAN)
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <BYTE-ORDER>MOST-SIGNIFICANT-BYTE-FIRST</BYTE-ORDER>
</SW-BASE-TYPE>''')

    def test_read_byte_order(self):
        xml = '''<SW-BASE-TYPE>
  <SHORT-NAME>Typename</SHORT-NAME>
  <BYTE-ORDER>MOST-SIGNIFICANT-BYTE-FIRST</BYTE-ORDER>
</SW-BASE-TYPE>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwBaseType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBaseType)
        self.assertEqual(elem.name, 'Typename')
        self.assertEqual(elem.byte_order, ar_enum.ByteOrder.BIG_ENDIAN)

    def test_write_sint8(self):
        element = ar_element.SwBaseType('sint8',
                                        category='FIXED_LENGTH',
                                        size=8,
                                        encoding='2C',
                                        native_declaration='sint8')
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-BASE-TYPE>
  <SHORT-NAME>sint8</SHORT-NAME>
  <CATEGORY>FIXED_LENGTH</CATEGORY>
  <BASE-TYPE-SIZE>8</BASE-TYPE-SIZE>
  <BASE-TYPE-ENCODING>2C</BASE-TYPE-ENCODING>
  <NATIVE-DECLARATION>sint8</NATIVE-DECLARATION>
</SW-BASE-TYPE>''')

    def test_read_byte_sint8(self):
        xml = '''
<SW-BASE-TYPE>
  <SHORT-NAME>sint8</SHORT-NAME>
  <CATEGORY>FIXED_LENGTH</CATEGORY>
  <BASE-TYPE-SIZE>8</BASE-TYPE-SIZE>
  <BASE-TYPE-ENCODING>2C</BASE-TYPE-ENCODING>
  <NATIVE-DECLARATION>sint8</NATIVE-DECLARATION>
</SW-BASE-TYPE>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwBaseType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBaseType)
        self.assertEqual(elem.name, 'sint8')
        self.assertEqual(elem.category, 'FIXED_LENGTH')
        self.assertEqual(elem.size, 8)
        self.assertEqual(elem.encoding, '2C')
        self.assertEqual(elem.native_declaration, 'sint8')


class TestSwAddrMethod(unittest.TestCase):

    def test_write_default(self):
        element = ar_element.SwAddrMethod('DEFAULT')
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-ADDR-METHOD>
  <SHORT-NAME>DEFAULT</SHORT-NAME>
</SW-ADDR-METHOD>''')

    def test_read_default(self):
        xml = '''<SW-ADDR-METHOD>
  <SHORT-NAME>DEFAULT</SHORT-NAME>
</SW-ADDR-METHOD>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwAddrMethod = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwAddrMethod)
        self.assertEqual(elem.name, 'DEFAULT')


class TestSwBaseTypeRef(unittest.TestCase):
    def test_write_default(self):
        element = ar_element.SwBaseTypeRef('/Package/ElementName')
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element),
                         '<BASE-TYPE-REF DEST="SW-BASE-TYPE">/Package/ElementName</BASE-TYPE-REF>')

    def test_read_default(self):
        xml = '<BASE-TYPE-REF DEST="SW-BASE-TYPE">/Package/ElementName</BASE-TYPE-REF>'
        reader = autosar.xml.Reader()
        elem: ar_element.SwBaseTypeRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBaseTypeRef)
        self.assertEqual(elem.value, '/Package/ElementName')


class TestSwBitRepresentation(unittest.TestCase):
    def test_write_empty(self):
        element = ar_element.SwBitRepresentation()
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element),
                         '<SW-BIT-REPRESENTATION/>')

    def test_read_empty(self):
        xml = '<SW-BIT-REPRESENTATION/>'
        reader = autosar.xml.Reader()
        elem: ar_element.SwBitRepresentation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBitRepresentation)

    def test_write_bit_position(self):
        element = ar_element.SwBitRepresentation(position=3)
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-BIT-REPRESENTATION>
  <BIT-POSITION>3</BIT-POSITION>
</SW-BIT-REPRESENTATION>''')

    def test_read_bit_position(self):
        xml = '''
<SW-BIT-REPRESENTATION>
  <BIT-POSITION>3</BIT-POSITION>
</SW-BIT-REPRESENTATION>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwBitRepresentation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBitRepresentation)
        self.assertEqual(elem.position, 3)

    def test_write_number_of_bits(self):
        element = ar_element.SwBitRepresentation(num_bits=1)
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '''<SW-BIT-REPRESENTATION>
  <NUMBER-OF-BITS>1</NUMBER-OF-BITS>
</SW-BIT-REPRESENTATION>''')

    def test_read__number_of_bits(self):
        xml = '''
<SW-BIT-REPRESENTATION>
  <NUMBER-OF-BITS>1</NUMBER-OF-BITS>
</SW-BIT-REPRESENTATION>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwBitRepresentation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwBitRepresentation)
        self.assertEqual(elem.num_bits, 1)


class TestSwTextProps(unittest.TestCase):

    def test_write_empty(self):
        element = ar_element.SwTextProps()
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element),
                         '<SW-TEXT-PROPS/>')

    def test_read_empty(self):
        xml = '<SW-TEXT-PROPS/>'
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)

    def test_write_array_size_semantics(self):
        element = ar_element.SwTextProps(array_size_semantics=ar_enum.ArraySizeSemantics.VARIABLE_SIZE)
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-TEXT-PROPS>
  <ARRAY-SIZE-SEMANTICS>VARIABLE-SIZE</ARRAY-SIZE-SEMANTICS>
</SW-TEXT-PROPS>''')

    def test_read_array_size_semantics(self):
        xml = '''<SW-TEXT-PROPS>
  <ARRAY-SIZE-SEMANTICS>VARIABLE-SIZE</ARRAY-SIZE-SEMANTICS>
</SW-TEXT-PROPS>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)
        self.assertEqual(elem.array_size_semantics, ar_enum.ArraySizeSemantics.VARIABLE_SIZE)

    def test_write_base_type_ref(self):
        element = ar_element.SwTextProps(base_type_ref=ar_element.SwBaseTypeRef('/Package/ElementName'))
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-TEXT-PROPS>
  <BASE-TYPE-REF DEST="SW-BASE-TYPE">/Package/ElementName</BASE-TYPE-REF>
</SW-TEXT-PROPS>''')

    def test_read_base_type_ref(self):
        xml = '''<SW-TEXT-PROPS>
  <BASE-TYPE-REF DEST="SW-BASE-TYPE">/Package/ElementName</BASE-TYPE-REF>
</SW-TEXT-PROPS>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)
        self.assertEqual(str(elem.base_type_ref), '/Package/ElementName')

    def test_write_fill_char(self):
        element = ar_element.SwTextProps(fill_char=0x30)
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-TEXT-PROPS>
  <SW-FILL-CHARACTER>48</SW-FILL-CHARACTER>
</SW-TEXT-PROPS>''')

    def test_read_fill_char(self):
        xml = '''<SW-TEXT-PROPS>
  <SW-FILL-CHARACTER>48</SW-FILL-CHARACTER>
</SW-TEXT-PROPS>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)
        self.assertEqual(elem.fill_char, 0x30)


class TestDataDefPropsConditional(unittest.TestCase):

    def test_write_empty(self):
        element = ar_element.SwDataDefPropsConditional()
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element),
                         '<SW-DATA-DEF-PROPS-CONDITIONAL/>')

    def test_read_empty(self):
        xml = '<SW-DATA-DEF-PROPS-CONDITIONAL/>'
        reader = autosar.xml.Reader()
        elem: ar_element.Annotation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)

    def test_write_display_presentation(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            display_presentation=ar_enum.DisplayPresentation.CONTINUOUS)
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <DISPLAY-PRESENTATION>PRESENTATION-CONTINUOUS</DISPLAY-PRESENTATION>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

        element = ar_element.SwDataDefPropsConditional(
            display_presentation=ar_enum.DisplayPresentation.DISCRETE)
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <DISPLAY-PRESENTATION>PRESENTATION-DISCRETE</DISPLAY-PRESENTATION>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_read_display_presentation(self):
        xml = '''
<SW-DATA-DEF-PROPS-CONDITIONAL>
  <DISPLAY-PRESENTATION>PRESENTATION-CONTINUOUS</DISPLAY-PRESENTATION>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.display_presentation,
                         ar_enum.DisplayPresentation.CONTINUOUS)

    def test_write_step_size(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(step_size=1)
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <STEP-SIZE>1</STEP-SIZE>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_read_step_size(self):
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <STEP-SIZE>1</STEP-SIZE>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.step_size, 1.0)

    def test_write_annotations(self):
        writer = autosar.xml.Writer()
        annotation = ar_element.Annotation(text=ar_element.DocumentationBlock(
            ar_element.MultiLanguageParagraph((ar_enum.Language.EN, 'Some Annotation'))))
        element = ar_element.SwDataDefPropsConditional(annotations=annotation)
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <ANNOTATIONS>
    <ANNOTATION>
      <ANNOTATION-TEXT>
        <P>
          <L-1 L="EN">Some Annotation</L-1>
        </P>
      </ANNOTATION-TEXT>
    </ANNOTATION>
  </ANNOTATIONS>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_read_annotations(self):
        xml = '''
<SW-DATA-DEF-PROPS-CONDITIONAL>
  <ANNOTATIONS>
    <ANNOTATION>
      <ANNOTATION-TEXT>
        <P>
          <L-1 L="EN">Some Annotation</L-1>
        </P>
      </ANNOTATION-TEXT>
    </ANNOTATION>
  </ANNOTATIONS>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        annotation = elem.annotations[0]
        self.assertIsInstance(annotation, ar_element.Annotation)
        annotation_text: ar_element.DocumentationBlock = annotation.text
        self.assertIsInstance(annotation_text, ar_element.DocumentationBlock)
        self.assertEqual(
            annotation_text.elements[0].elements[0].parts[0], "Some Annotation")
        self.assertEqual(
            annotation_text.elements[0].elements[0].language, ar_enum.Language.EN)

    def test_write_sw_addr_method_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            sw_addr_method_ref=ar_element.SwAddrMethodRef('/SwAddrMethods/DEFAULT'))
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ADDR-METHOD-REF DEST="SW-ADDR-METHOD">/SwAddrMethods/DEFAULT</SW-ADDR-METHOD-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_write_sw_addr_method_ref_implicit(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            sw_addr_method_ref='/SwAddrMethods/DEFAULT')
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ADDR-METHOD-REF DEST="SW-ADDR-METHOD">/SwAddrMethods/DEFAULT</SW-ADDR-METHOD-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_read_sw_addr_method_ref(self):
        xml = '''
<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ADDR-METHOD-REF DEST="SW-ADDR-METHOD">/SwAddrMethods/DEFAULT</SW-ADDR-METHOD-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        ref = elem.sw_addr_method_ref
        self.assertEqual(ref.value, '/SwAddrMethods/DEFAULT')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD)

    def test_write_sw_alignment_int(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(alignment=16)
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>16</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_read_sw_alignment_int(self):
        xml = '''
<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>16</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.alignment, 16)

    def test_write_sw_alignment_hex_str(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(alignment='0x800')
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>0x800</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_write_sw_alignment_unspecified(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(alignment='UNSPECIFIED')
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>UNSPECIFIED</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_write_sw_alignment_ptr(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(alignment='PTR')
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>PTR</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_read_sw_alignment_ptr(self):
        xml = '''
<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>PTR</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.alignment, "PTR")

    def test_write_base_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(base_type_ref='/BaseTypes/TypeName')
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <BASE-TYPE-REF DEST="SW-BASE-TYPE">/BaseTypes/TypeName</BASE-TYPE-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_read_base_ref(self):
        xml = '''
<SW-DATA-DEF-PROPS-CONDITIONAL>
  <BASE-TYPE-REF DEST="SW-BASE-TYPE">/BaseTypes/TypeName</BASE-TYPE-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        ref = elem.base_type_ref
        self.assertEqual(ref.value, '/BaseTypes/TypeName')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.SW_BASE_TYPE)

    def test_write_sw_bit_representation(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            bit_representation=ar_element.SwBitRepresentation(position=1, num_bits=2))
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-BIT-REPRESENTATION>
    <BIT-POSITION>1</BIT-POSITION>
    <NUMBER-OF-BITS>2</NUMBER-OF-BITS>
  </SW-BIT-REPRESENTATION>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_read_sw_bit_representation(self):
        xml = '''
<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-BIT-REPRESENTATION>
    <BIT-POSITION>1</BIT-POSITION>
    <NUMBER-OF-BITS>2</NUMBER-OF-BITS>
  </SW-BIT-REPRESENTATION>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        child_elem: ar_element.SwBitRepresentation = elem.bit_representation
        self.assertEqual(child_elem.position, 1)
        self.assertEqual(child_elem.num_bits, 2)

    def test_write_sw_calibration_access(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            calibration_access=ar_enum.SwCalibrationAccess.READ_ONLY)
        self.assertEqual(writer.write_str_elem(element),
                         '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-CALIBRATION-ACCESS>READ-ONLY</SW-CALIBRATION-ACCESS>
</SW-DATA-DEF-PROPS-CONDITIONAL>''')

    def test_read_sw_calibration_access(self):
        xml = '''
<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-CALIBRATION-ACCESS>READ-ONLY</SW-CALIBRATION-ACCESS>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.calibration_access, ar_enum.SwCalibrationAccess.READ_ONLY)


if __name__ == '__main__':
    unittest.main()
