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

    def test_read_write_empty(self):
        element = ar_element.SwTextProps()
        writer = autosar.xml.Writer()
        xml = '<SW-TEXT-PROPS/>'
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)

    def test_read_write_array_size_semantics(self):
        element = ar_element.SwTextProps(array_size_semantics=ar_enum.ArraySizeSemantics.VARIABLE_SIZE)
        writer = autosar.xml.Writer()
        xml = '''<SW-TEXT-PROPS>
  <ARRAY-SIZE-SEMANTICS>VARIABLE-SIZE</ARRAY-SIZE-SEMANTICS>
</SW-TEXT-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)
        self.assertEqual(elem.array_size_semantics, ar_enum.ArraySizeSemantics.VARIABLE_SIZE)

    def test_read_write_max_text_size(self):
        element = ar_element.SwTextProps(max_text_size=32)
        writer = autosar.xml.Writer()
        xml = '''<SW-TEXT-PROPS>
  <SW-MAX-TEXT-SIZE>32</SW-MAX-TEXT-SIZE>
</SW-TEXT-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)
        self.assertEqual(elem.max_text_size, 32)

    def test_read_write_base_type_ref(self):
        element = ar_element.SwTextProps(base_type_ref=ar_element.SwBaseTypeRef('/Package/ElementName'))
        writer = autosar.xml.Writer()
        xml = '''<SW-TEXT-PROPS>
  <BASE-TYPE-REF DEST="SW-BASE-TYPE">/Package/ElementName</BASE-TYPE-REF>
</SW-TEXT-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)
        self.assertEqual(str(elem.base_type_ref), '/Package/ElementName')

    def test_read_write_fill_char(self):
        """
        Not yet possible to choose integer base in Writer output
        for selected elements. Use to decimal for now.
        """
        element = ar_element.SwTextProps(fill_char=0x30)
        writer = autosar.xml.Writer()
        xml = '''<SW-TEXT-PROPS>
  <SW-FILL-CHARACTER>48</SW-FILL-CHARACTER>
</SW-TEXT-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)
        self.assertEqual(elem.fill_char, 0x30)

    def test_read_hex_literal_fill_char(self):
        """
        Verify that we can process fill-char when
        expressed as hex-literal
        """
        xml = '''<SW-TEXT-PROPS>
  <SW-FILL-CHARACTER>0x30</SW-FILL-CHARACTER>
</SW-TEXT-PROPS>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwTextProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwTextProps)
        self.assertEqual(elem.fill_char, 0x30)


class TestSwPointerTargetProps(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.SwPointerTargetProps()
        writer = autosar.xml.Writer()
        xml = '<SW-POINTER-TARGET-PROPS/>'
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.Annotation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwPointerTargetProps)

    def test_read_write_target_category(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwPointerTargetProps(target_category="DATA")
        xml = '''<SW-POINTER-TARGET-PROPS>
  <TARGET-CATEGORY>DATA</TARGET-CATEGORY>
</SW-POINTER-TARGET-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwPointerTargetProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwPointerTargetProps)
        self.assertEqual(elem.target_category, "DATA")

    def test_read_write_function_ptr_signagure_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwPointerTargetProps(function_ptr_signature_ref="/BSW/FunctionName")
        xml = '''<SW-POINTER-TARGET-PROPS>
  <FUNCTION-POINTER-SIGNATURE-REF DEST="BSW-MODULE-ENTRY">/BSW/FunctionName</FUNCTION-POINTER-SIGNATURE-REF>
</SW-POINTER-TARGET-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwPointerTargetProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwPointerTargetProps)
        ref = elem.function_ptr_signature_ref
        self.assertEqual(ref.value, '/BSW/FunctionName')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.BSW_MODULE_ENTRY)


class TestDataDefPropsConditional(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.SwDataDefPropsConditional()
        writer = autosar.xml.Writer()
        xml = '<SW-DATA-DEF-PROPS-CONDITIONAL/>'
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.Annotation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)

    def test_read_write_display_presentation_continous(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            display_presentation=ar_enum.DisplayPresentation.CONTINUOUS)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <DISPLAY-PRESENTATION>PRESENTATION-CONTINUOUS</DISPLAY-PRESENTATION>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.display_presentation,
                         ar_enum.DisplayPresentation.CONTINUOUS)

    def test_read_write_display_presentation_discrete(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            display_presentation=ar_enum.DisplayPresentation.DISCRETE)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <DISPLAY-PRESENTATION>PRESENTATION-DISCRETE</DISPLAY-PRESENTATION>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.display_presentation,
                         ar_enum.DisplayPresentation.DISCRETE)

    def test_read_write_step_size(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(step_size=1)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <STEP-SIZE>1</STEP-SIZE>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.step_size, 1.0)

    def test_read_write_annotations(self):
        writer = autosar.xml.Writer()
        annotation = ar_element.Annotation(text=ar_element.DocumentationBlock(
            ar_element.MultiLanguageParagraph((ar_enum.Language.EN, 'Some Annotation'))))
        element = ar_element.SwDataDefPropsConditional(annotations=annotation)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
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
        self.assertEqual(writer.write_str_elem(element), xml)
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

    def test_read_write_sw_addr_method_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            sw_addr_method_ref=ar_element.SwAddrMethodRef('/SwAddrMethods/DEFAULT'))
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ADDR-METHOD-REF DEST="SW-ADDR-METHOD">/SwAddrMethods/DEFAULT</SW-ADDR-METHOD-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        ref = elem.sw_addr_method_ref
        self.assertEqual(ref.value, '/SwAddrMethods/DEFAULT')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD)

    def test_write_sw_addr_method_ref_from_string(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            sw_addr_method_ref='/SwAddrMethods/DEFAULT')
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ADDR-METHOD-REF DEST="SW-ADDR-METHOD">/SwAddrMethods/DEFAULT</SW-ADDR-METHOD-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)

    def test_read_write_sw_alignment_int(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(alignment=16)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>16</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.alignment, 16)

    def test_write_sw_alignment_hex_str(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(alignment='0x800')
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>0x800</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)

    def test_write_sw_alignment_unspecified(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(alignment='UNSPECIFIED')
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>UNSPECIFIED</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)

    def test_read_write_sw_alignment_ptr(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(alignment='PTR')
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-ALIGNMENT>PTR</SW-ALIGNMENT>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.alignment, "PTR")

    def test_read_write_base_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(base_type_ref='/BaseTypes/TypeName')
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <BASE-TYPE-REF DEST="SW-BASE-TYPE">/BaseTypes/TypeName</BASE-TYPE-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        ref = elem.base_type_ref
        self.assertEqual(ref.value, '/BaseTypes/TypeName')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.SW_BASE_TYPE)

    def test_read_write_sw_bit_representation(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            bit_representation=ar_element.SwBitRepresentation(position=1, num_bits=2))
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-BIT-REPRESENTATION>
    <BIT-POSITION>1</BIT-POSITION>
    <NUMBER-OF-BITS>2</NUMBER-OF-BITS>
  </SW-BIT-REPRESENTATION>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        child_elem: ar_element.SwBitRepresentation = elem.bit_representation
        self.assertEqual(child_elem.position, 1)
        self.assertEqual(child_elem.num_bits, 2)

    def test_read_write_sw_calibration_access(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            calibration_access=ar_enum.SwCalibrationAccess.READ_ONLY)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-CALIBRATION-ACCESS>READ-ONLY</SW-CALIBRATION-ACCESS>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.calibration_access, ar_enum.SwCalibrationAccess.READ_ONLY)

    def test_read_write_sw_text_props(self):
        writer = autosar.xml.Writer()
        text_props = ar_element.SwTextProps(array_size_semantics=ar_enum.ArraySizeSemantics.VARIABLE_SIZE,
                                            max_text_size=128,
                                            fill_char=0x30)
        element = ar_element.SwDataDefPropsConditional(text_props=text_props)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-TEXT-PROPS>
    <ARRAY-SIZE-SEMANTICS>VARIABLE-SIZE</ARRAY-SIZE-SEMANTICS>
    <SW-MAX-TEXT-SIZE>128</SW-MAX-TEXT-SIZE>
    <SW-FILL-CHARACTER>48</SW-FILL-CHARACTER>
  </SW-TEXT-PROPS>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)

        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        props: ar_element.SwTextProps = elem.text_props
        self.assertEqual(props.array_size_semantics, ar_enum.ArraySizeSemantics.VARIABLE_SIZE)
        self.assertEqual(props.max_text_size, 128)
        self.assertEqual(props.fill_char, 0x30)

    def test_read_write_compu_method_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(compu_method_ref='/CompuMethods/CompuName')
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <COMPU-METHOD-REF DEST="COMPU-METHOD">/CompuMethods/CompuName</COMPU-METHOD-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        ref = elem.compu_method_ref
        self.assertIsInstance(ref, ar_element.CompuMethodRef)
        self.assertEqual(ref.value, '/CompuMethods/CompuName')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.COMPU_METHOD)

    def test_read_write_data_constraint_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(data_constraint_ref='/DataConstraints/ConstraintName')
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <DATA-CONSTR-REF DEST="DATA-CONSTR">/DataConstraints/ConstraintName</DATA-CONSTR-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        ref = elem.data_constraint_ref
        self.assertIsInstance(ref, ar_element.DataConstraintRef)
        self.assertEqual(ref.value, '/DataConstraints/ConstraintName')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.DATA_CONSTR)

    def test_read_write_impl_data_type_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(impl_data_type_ref='/DataTypes/TypeName')
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/TypeName</IMPLEMENTATION-DATA-TYPE-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        ref = elem.impl_data_type_ref
        self.assertIsInstance(ref, ar_element.ImplementationDataTypeRef)
        self.assertEqual(ref.value, '/DataTypes/TypeName')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)

    def test_read_write_unit_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(unit_ref='/Units/Kelvin')
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <UNIT-REF DEST="UNIT">/Units/Kelvin</UNIT-REF>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        ref = elem.unit_ref
        self.assertIsInstance(ref, ar_element.UnitRef)
        self.assertEqual(ref.value, '/Units/Kelvin')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.UNIT)

    def test_read_write_display_format(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(display_format=r'%.02f')
        xml = r'''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <DISPLAY-FORMAT>%.02f</DISPLAY-FORMAT>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.display_format, r'%.02f')

    def test_read_write_impl_policy(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            impl_policy=ar_enum.SwImplPolicy.MEASUREMENT_POINT)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-IMPL-POLICY>MEASUREMENT-POINT</SW-IMPL-POLICY>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.impl_policy, ar_enum.SwImplPolicy.MEASUREMENT_POINT)

    def test_read_write_additional_native_type_qualifier(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(
            additional_native_type_qualifier="volatile")
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <ADDITIONAL-NATIVE-TYPE-QUALIFIER>volatile</ADDITIONAL-NATIVE-TYPE-QUALIFIER>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.additional_native_type_qualifier, "volatile")

    def test_read_write_intended_resolution(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(intended_resolution=0.03125)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-INTENDED-RESOLUTION>0.03125</SW-INTENDED-RESOLUTION>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.intended_resolution, 0.03125)

    def test_read_write_interpolation_method(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(interpolation_method="STEPWISE-LINEAR")
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-INTERPOLATION-METHOD>STEPWISE-LINEAR</SW-INTERPOLATION-METHOD>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertEqual(elem.interpolation_method, "STEPWISE-LINEAR")

    def test_read_write_is_virtual(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwDataDefPropsConditional(is_virtual=True)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-IS-VIRTUAL>true</SW-IS-VIRTUAL>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        self.assertTrue(elem.is_virtual)

    def test_read_write_sw_pointer_target_props(self):
        writer = autosar.xml.Writer()
        sw_props = ar_element.SwPointerTargetProps(target_category="MY-CATEGORY")
        element = ar_element.SwDataDefPropsConditional(ptr_target_props=sw_props)
        xml = '''<SW-DATA-DEF-PROPS-CONDITIONAL>
  <SW-POINTER-TARGET-PROPS>
    <TARGET-CATEGORY>MY-CATEGORY</TARGET-CATEGORY>
  </SW-POINTER-TARGET-PROPS>
</SW-DATA-DEF-PROPS-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwDataDefPropsConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwDataDefPropsConditional)
        props = elem.ptr_target_props
        self.assertEqual(props.target_category, "MY-CATEGORY")


class TestSymbolProps(unittest.TestCase):

    def test_read_write_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.SymbolProps('MyName')
        xml = '''<SYMBOL-PROPS>
  <SHORT-NAME>MyName</SHORT-NAME>
</SYMBOL-PROPS>'''
        self.assertEqual(writer.write_str_elem(element, "SYMBOL-PROPS"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SymbolProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SymbolProps)
        self.assertEqual(elem.name, 'MyName')
        self.assertEqual(elem.short_name, 'MyName')

    def test_read_write_symbol(self):
        writer = autosar.xml.Writer()
        element = ar_element.SymbolProps('MyName', symbol="Symbol")
        xml = '''<SYMBOL-PROPS>
  <SHORT-NAME>MyName</SHORT-NAME>
  <SYMBOL>Symbol</SYMBOL>
</SYMBOL-PROPS>'''
        self.assertEqual(writer.write_str_elem(element, "SYMBOL-PROPS"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SymbolProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SymbolProps)
        self.assertEqual(elem.name, 'MyName')
        self.assertEqual(elem.symbol, 'Symbol')


class TestImplementationDataTypeElement(unittest.TestCase):

    def test_read_write_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataTypeElement('ElementName')
        xml = '''<IMPLEMENTATION-DATA-TYPE-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
</IMPLEMENTATION-DATA-TYPE-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataTypeElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(elem.name, 'ElementName')
        self.assertEqual(elem.short_name, 'ElementName')

    def test_read_write_array_impl_policy(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataTypeElement('ElementName',
                    array_impl_policy=ar_enum.ArrayImplPolicy.PAYLOAD_AS_POINTER_TO_ARRAY)  # noqa E128
        xml = '''<IMPLEMENTATION-DATA-TYPE-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <ARRAY-IMPL-POLICY>PAYLOAD-AS-POINTER-TO-ARRAY</ARRAY-IMPL-POLICY>
</IMPLEMENTATION-DATA-TYPE-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataTypeElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(elem.name, 'ElementName')
        self.assertEqual(elem.array_impl_policy, ar_enum.ArrayImplPolicy.PAYLOAD_AS_POINTER_TO_ARRAY)

    def test_read_write_array_size(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataTypeElement('ElementName',
                                                           array_size=10)
        xml = '''<IMPLEMENTATION-DATA-TYPE-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <ARRAY-SIZE>10</ARRAY-SIZE>
</IMPLEMENTATION-DATA-TYPE-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataTypeElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(elem.name, 'ElementName')
        self.assertEqual(elem.array_size, 10)

    def test_read_write_array_size_handling(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataTypeElement('ElementName',
                                              array_size_handling=ar_enum.ArraySizeHandling.ALL_INDICES_SAME_ARRAY_SIZE) # noqa E128 #pylint: disable=C0301
        xml = '''<IMPLEMENTATION-DATA-TYPE-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <ARRAY-SIZE-HANDLING>ALL-INDICES-SAME-ARRAY-SIZE</ARRAY-SIZE-HANDLING>
</IMPLEMENTATION-DATA-TYPE-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataTypeElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(elem.name, 'ElementName')
        self.assertEqual(elem.array_size_handling, ar_enum.ArraySizeHandling.ALL_INDICES_SAME_ARRAY_SIZE)

    def test_read_write_array_size_semantics(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataTypeElement('ElementName',
                                              array_size_semantics=ar_enum.ArraySizeSemantics.FIXED_SIZE) # noqa E128
        xml = '''<IMPLEMENTATION-DATA-TYPE-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <ARRAY-SIZE-SEMANTICS>FIXED-SIZE</ARRAY-SIZE-SEMANTICS>
</IMPLEMENTATION-DATA-TYPE-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataTypeElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(elem.name, 'ElementName')
        self.assertEqual(elem.array_size_semantics, ar_enum.ArraySizeSemantics.FIXED_SIZE)

    def test_read_write_is_optional(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataTypeElement('ElementName',
                                                           is_optional=True) # noqa E501
        xml = '''<IMPLEMENTATION-DATA-TYPE-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <IS-OPTIONAL>true</IS-OPTIONAL>
</IMPLEMENTATION-DATA-TYPE-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataTypeElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(elem.name, 'ElementName')
        self.assertTrue(elem.is_optional)

    def test_read_write_sub_elements(self):
        writer = autosar.xml.Writer()
        child1 = ar_element.ImplementationDataTypeElement('Child1', array_size=4)
        child2 = ar_element.ImplementationDataTypeElement('Child2', array_size=8, category="MyCategory")
        element = ar_element.ImplementationDataTypeElement('ElementName',
                                                           sub_elements=[child1, child2])

        xml = '''<IMPLEMENTATION-DATA-TYPE-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <SUB-ELEMENTS>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Child1</SHORT-NAME>
      <ARRAY-SIZE>4</ARRAY-SIZE>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Child2</SHORT-NAME>
      <CATEGORY>MyCategory</CATEGORY>
      <ARRAY-SIZE>8</ARRAY-SIZE>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
  </SUB-ELEMENTS>
</IMPLEMENTATION-DATA-TYPE-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataTypeElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertEqual(len(elem.sub_elements), 2)
        sub_elem = elem.sub_elements[0]
        self.assertEqual(sub_elem.name, "Child1")
        self.assertEqual(sub_elem.array_size, 4)
        sub_elem = elem.sub_elements[1]
        self.assertEqual(sub_elem.name, "Child2")
        self.assertEqual(sub_elem.array_size, 8)
        self.assertEqual(sub_elem.category, "MyCategory")

    def test_read_write_sw_data_def_props(self):
        writer = autosar.xml.Writer()
        uint8_ref = "/PlatformTypes/uint8"
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=ar_element.SwBaseTypeRef(uint8_ref))
        element = ar_element.ImplementationDataTypeElement('ElementName',
                                                           sw_data_def_props = sw_data_def_props) # noqa E501
        xml = '''<IMPLEMENTATION-DATA-TYPE-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <SW-DATA-DEF-PROPS>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <BASE-TYPE-REF DEST="SW-BASE-TYPE">/PlatformTypes/uint8</BASE-TYPE-REF>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </SW-DATA-DEF-PROPS>
</IMPLEMENTATION-DATA-TYPE-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataTypeElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(elem.name, 'ElementName')
        self.assertEqual(len(elem.sw_data_def_props), 1)
        self.assertEqual(str(elem.sw_data_def_props[0].base_type_ref), uint8_ref)


class TestImplementationDataType(unittest.TestCase):

    def test_read_write_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataType('TypeName')
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
</IMPLEMENTATION-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'TypeName')

    def test_read_write_dynamic_array_size_profile(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataType('TypeName',
                                                    dynamic_array_size_profile="Profile")
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <DYNAMIC-ARRAY-SIZE-PROFILE>Profile</DYNAMIC-ARRAY-SIZE-PROFILE>
</IMPLEMENTATION-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'TypeName')
        self.assertEqual(elem.dynamic_array_size_profile, "Profile")

    def test_read_write_is_struct_with_optional_element(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataType('TypeName',
                                                    is_struct_with_optional_element=True)
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <IS-STRUCT-WITH-OPTIONAL-ELEMENT>true</IS-STRUCT-WITH-OPTIONAL-ELEMENT>
</IMPLEMENTATION-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'TypeName')
        self.assertTrue(elem.is_struct_with_optional_element)

    def test_read_write_sub_elements(self):
        writer = autosar.xml.Writer()
        child1 = ar_element.ImplementationDataTypeElement('Child1', array_size=4)
        child2 = ar_element.ImplementationDataTypeElement('Child2', array_size=8)
        element = ar_element.ImplementationDataType('TypeName',
                                                    sub_elements=[child1, child2])
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <SUB-ELEMENTS>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Child1</SHORT-NAME>
      <ARRAY-SIZE>4</ARRAY-SIZE>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Child2</SHORT-NAME>
      <ARRAY-SIZE>8</ARRAY-SIZE>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
  </SUB-ELEMENTS>
</IMPLEMENTATION-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'TypeName')
        self.assertEqual(len(elem.sub_elements), 2)
        sub_elem = elem.sub_elements[0]
        self.assertEqual(sub_elem.name, "Child1")
        self.assertEqual(sub_elem.array_size, 4)
        sub_elem = elem.sub_elements[1]
        self.assertEqual(sub_elem.name, "Child2")
        self.assertEqual(sub_elem.array_size, 8)

    def test_read_write_symbol_props(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataType("TypeName",
                                                    symbol_props=ar_element.SymbolProps("TypeName", "Symbol"))
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <SYMBOL-PROPS>
    <SHORT-NAME>TypeName</SHORT-NAME>
    <SYMBOL>Symbol</SYMBOL>
  </SYMBOL-PROPS>
</IMPLEMENTATION-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, "TypeName")
        self.assertEqual(elem.symbol_props.name, "TypeName")
        self.assertEqual(elem.symbol_props.symbol, "Symbol")

    def test_read_write_type_emitter(self):
        writer = autosar.xml.Writer()
        element = ar_element.ImplementationDataType('TypeName',
                                                    type_emitter="RTE")
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <TYPE-EMITTER>RTE</TYPE-EMITTER>
</IMPLEMENTATION-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'TypeName')
        self.assertEqual(elem.type_emitter, "RTE")

    def test_read_sw_data_def_props(self):
        writer = autosar.xml.Writer()
        uint8_ref = "/PlatformTypes/uint8"
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=ar_element.SwBaseTypeRef(uint8_ref))
        element = ar_element.ImplementationDataType('TypeName',
                                                    sw_data_def_props=sw_data_def_props)
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <SW-DATA-DEF-PROPS>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <BASE-TYPE-REF DEST="SW-BASE-TYPE">/PlatformTypes/uint8</BASE-TYPE-REF>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </SW-DATA-DEF-PROPS>
</IMPLEMENTATION-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'TypeName')
        self.assertEqual(len(elem.sw_data_def_props), 1)
        self.assertEqual(str(elem.sw_data_def_props[0].base_type_ref), uint8_ref)


class TestCompleteImplementationDataType(unittest.TestCase):

    def test_array_data_type_with_value_element(self):
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="/DataTypes/BaseTypes/uint8")
        sub_element = ar_element.ImplementationDataTypeElement("Element",
                                                               category="VALUE",
                                                               array_size=4,
                                                               sw_data_def_props=sw_data_def_props)
        element = ar_element.ImplementationDataType("U8Buf4_T",
                                                    category="ARRAY",
                                                    sub_elements=[sub_element])
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>U8Buf4_T</SHORT-NAME>
  <CATEGORY>ARRAY</CATEGORY>
  <SUB-ELEMENTS>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Element</SHORT-NAME>
      <CATEGORY>VALUE</CATEGORY>
      <ARRAY-SIZE>4</ARRAY-SIZE>
      <SW-DATA-DEF-PROPS>
        <SW-DATA-DEF-PROPS-VARIANTS>
          <SW-DATA-DEF-PROPS-CONDITIONAL>
            <BASE-TYPE-REF DEST="SW-BASE-TYPE">/DataTypes/BaseTypes/uint8</BASE-TYPE-REF>
          </SW-DATA-DEF-PROPS-CONDITIONAL>
        </SW-DATA-DEF-PROPS-VARIANTS>
      </SW-DATA-DEF-PROPS>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
  </SUB-ELEMENTS>
</IMPLEMENTATION-DATA-TYPE>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'U8Buf4_T')
        sub_elem = elem.find("Element")
        self.assertIsInstance(sub_elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(sub_elem.name, "Element")

    def test_array_data_type_with_ref_type_element(self):
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref="/DataTypes/InactiveActive_T")
        sub_element = ar_element.ImplementationDataTypeElement("Element",
                                                               category="TYPE_REFERENCE",
                                                               array_size=2,
                                                               sw_data_def_props=sw_data_def_props)
        element = ar_element.ImplementationDataType("InactiveActiveArray2_T",
                                                    category="ARRAY",
                                                    sub_elements=[sub_element])
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>InactiveActiveArray2_T</SHORT-NAME>
  <CATEGORY>ARRAY</CATEGORY>
  <SUB-ELEMENTS>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Element</SHORT-NAME>
      <CATEGORY>TYPE_REFERENCE</CATEGORY>
      <ARRAY-SIZE>2</ARRAY-SIZE>
      <SW-DATA-DEF-PROPS>
        <SW-DATA-DEF-PROPS-VARIANTS>
          <SW-DATA-DEF-PROPS-CONDITIONAL>
            <IMPLEMENTATION-DATA-TYPE-REF \
DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/InactiveActive_T</IMPLEMENTATION-DATA-TYPE-REF>
          </SW-DATA-DEF-PROPS-CONDITIONAL>
        </SW-DATA-DEF-PROPS-VARIANTS>
      </SW-DATA-DEF-PROPS>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
  </SUB-ELEMENTS>
</IMPLEMENTATION-DATA-TYPE>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'InactiveActiveArray2_T')
        sub_elem = elem.find("Element")
        self.assertIsInstance(sub_elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(sub_elem.name, "Element")

    def test_struct_data_type_with_value_elements(self):
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="/DataTypes/BaseTypes/uint8")
        elem1 = ar_element.ImplementationDataTypeElement("Elem1",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="/DataTypes/BaseTypes/uint32")
        elem2 = ar_element.ImplementationDataTypeElement("Elem2",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
        element = ar_element.ImplementationDataType("RecordType_T",
                                                    category="STRUCTURE",
                                                    sub_elements=[elem1, elem2])
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>RecordType_T</SHORT-NAME>
  <CATEGORY>STRUCTURE</CATEGORY>
  <SUB-ELEMENTS>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Elem1</SHORT-NAME>
      <CATEGORY>VALUE</CATEGORY>
      <SW-DATA-DEF-PROPS>
        <SW-DATA-DEF-PROPS-VARIANTS>
          <SW-DATA-DEF-PROPS-CONDITIONAL>
            <BASE-TYPE-REF DEST="SW-BASE-TYPE">/DataTypes/BaseTypes/uint8</BASE-TYPE-REF>
          </SW-DATA-DEF-PROPS-CONDITIONAL>
        </SW-DATA-DEF-PROPS-VARIANTS>
      </SW-DATA-DEF-PROPS>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Elem2</SHORT-NAME>
      <CATEGORY>VALUE</CATEGORY>
      <SW-DATA-DEF-PROPS>
        <SW-DATA-DEF-PROPS-VARIANTS>
          <SW-DATA-DEF-PROPS-CONDITIONAL>
            <BASE-TYPE-REF DEST="SW-BASE-TYPE">/DataTypes/BaseTypes/uint32</BASE-TYPE-REF>
          </SW-DATA-DEF-PROPS-CONDITIONAL>
        </SW-DATA-DEF-PROPS-VARIANTS>
      </SW-DATA-DEF-PROPS>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
  </SUB-ELEMENTS>
</IMPLEMENTATION-DATA-TYPE>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'RecordType_T')
        sub_elem = elem.find("Elem1")
        self.assertIsInstance(sub_elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(sub_elem.name, "Elem1")
        sub_elem = elem.find("Elem2")
        self.assertIsInstance(sub_elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(sub_elem.name, "Elem2")

    def test_struct_data_type_with_ref_type_elements(self):
        sw_data_def_props = ar_element.SwDataDefPropsConditional(
            impl_data_type_ref="/AUTOSAR_Platform/ImplementationTypes/uint8")
        elem1 = ar_element.ImplementationDataTypeElement("Elem1",
                                                         category="TYPE_REFERENCE",
                                                         sw_data_def_props=sw_data_def_props)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(
            impl_data_type_ref="/AUTOSAR_Platform/ImplementationTypes/uint32")
        elem2 = ar_element.ImplementationDataTypeElement("Elem2",
                                                         category="TYPE_REFERENCE",
                                                         sw_data_def_props=sw_data_def_props)
        element = ar_element.ImplementationDataType("RecordType_T",
                                                    category="STRUCTURE",
                                                    sub_elements=[elem1, elem2])
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>RecordType_T</SHORT-NAME>
  <CATEGORY>STRUCTURE</CATEGORY>
  <SUB-ELEMENTS>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Elem1</SHORT-NAME>
      <CATEGORY>TYPE_REFERENCE</CATEGORY>
      <SW-DATA-DEF-PROPS>
        <SW-DATA-DEF-PROPS-VARIANTS>
          <SW-DATA-DEF-PROPS-CONDITIONAL>
            <IMPLEMENTATION-DATA-TYPE-REF \
DEST="IMPLEMENTATION-DATA-TYPE">/AUTOSAR_Platform/ImplementationTypes/uint8</IMPLEMENTATION-DATA-TYPE-REF>
          </SW-DATA-DEF-PROPS-CONDITIONAL>
        </SW-DATA-DEF-PROPS-VARIANTS>
      </SW-DATA-DEF-PROPS>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
    <IMPLEMENTATION-DATA-TYPE-ELEMENT>
      <SHORT-NAME>Elem2</SHORT-NAME>
      <CATEGORY>TYPE_REFERENCE</CATEGORY>
      <SW-DATA-DEF-PROPS>
        <SW-DATA-DEF-PROPS-VARIANTS>
          <SW-DATA-DEF-PROPS-CONDITIONAL>
            <IMPLEMENTATION-DATA-TYPE-REF \
DEST="IMPLEMENTATION-DATA-TYPE">/AUTOSAR_Platform/ImplementationTypes/uint32</IMPLEMENTATION-DATA-TYPE-REF>
          </SW-DATA-DEF-PROPS-CONDITIONAL>
        </SW-DATA-DEF-PROPS-VARIANTS>
      </SW-DATA-DEF-PROPS>
    </IMPLEMENTATION-DATA-TYPE-ELEMENT>
  </SUB-ELEMENTS>
</IMPLEMENTATION-DATA-TYPE>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'RecordType_T')
        sub_elem: ar_element.ImplementationDataTypeElement = elem.find("Elem1")
        self.assertIsInstance(sub_elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(sub_elem.name, "Elem1")
        self.assertEqual(str(sub_elem.sw_data_def_props[0].impl_data_type_ref),
                         "/AUTOSAR_Platform/ImplementationTypes/uint8")
        sub_elem: ar_element.ImplementationDataTypeElement = elem.find("Elem2")
        self.assertIsInstance(sub_elem, ar_element.ImplementationDataTypeElement)
        self.assertEqual(sub_elem.name, "Elem2")
        self.assertEqual(str(sub_elem.sw_data_def_props[0].impl_data_type_ref),
                         "/AUTOSAR_Platform/ImplementationTypes/uint32")

    def test_pointer_data_type_to_value_type(self):
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="/DataTypes/BaseTypes/uint8")
        pointer_target_props = ar_element.SwPointerTargetProps("VALUE", sw_data_def_props)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(ptr_target_props=pointer_target_props)
        element = ar_element.ImplementationDataType("dataPtr_T",
                                                    category="DATA_REFERENCE",
                                                    sw_data_def_props=sw_data_def_props
                                                    )
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>dataPtr_T</SHORT-NAME>
  <CATEGORY>DATA_REFERENCE</CATEGORY>
  <SW-DATA-DEF-PROPS>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <SW-POINTER-TARGET-PROPS>
          <TARGET-CATEGORY>VALUE</TARGET-CATEGORY>
          <SW-DATA-DEF-PROPS>
            <SW-DATA-DEF-PROPS-VARIANTS>
              <SW-DATA-DEF-PROPS-CONDITIONAL>
                <BASE-TYPE-REF DEST="SW-BASE-TYPE">/DataTypes/BaseTypes/uint8</BASE-TYPE-REF>
              </SW-DATA-DEF-PROPS-CONDITIONAL>
            </SW-DATA-DEF-PROPS-VARIANTS>
          </SW-DATA-DEF-PROPS>
        </SW-POINTER-TARGET-PROPS>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </SW-DATA-DEF-PROPS>
</IMPLEMENTATION-DATA-TYPE>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'dataPtr_T')
        ptr_target_props = elem.sw_data_def_props[0].ptr_target_props
        self.assertEqual(ptr_target_props.target_category, "VALUE")
        sw_data_def_props = ptr_target_props.sw_data_def_props
        self.assertEqual(str(sw_data_def_props[0].base_type_ref), "/DataTypes/BaseTypes/uint8")

    def test_pointer_data_type_to_ref_type(self):
        sw_data_def_props = ar_element.SwDataDefPropsConditional(
            impl_data_type_ref="/DataTypes/ImplementationTypes/InactiveActive_T")
        pointer_target_props = ar_element.SwPointerTargetProps("TYPE_REFERENCE", sw_data_def_props)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(ptr_target_props=pointer_target_props)
        element = ar_element.ImplementationDataType("dataPtr_T",
                                                    category="DATA_REFERENCE",
                                                    sw_data_def_props=sw_data_def_props
                                                    )
        xml = '''<IMPLEMENTATION-DATA-TYPE>
  <SHORT-NAME>dataPtr_T</SHORT-NAME>
  <CATEGORY>DATA_REFERENCE</CATEGORY>
  <SW-DATA-DEF-PROPS>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <SW-POINTER-TARGET-PROPS>
          <TARGET-CATEGORY>TYPE_REFERENCE</TARGET-CATEGORY>
          <SW-DATA-DEF-PROPS>
            <SW-DATA-DEF-PROPS-VARIANTS>
              <SW-DATA-DEF-PROPS-CONDITIONAL>
                <IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">\
/DataTypes/ImplementationTypes/InactiveActive_T</IMPLEMENTATION-DATA-TYPE-REF>
              </SW-DATA-DEF-PROPS-CONDITIONAL>
            </SW-DATA-DEF-PROPS-VARIANTS>
          </SW-DATA-DEF-PROPS>
        </SW-POINTER-TARGET-PROPS>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </SW-DATA-DEF-PROPS>
</IMPLEMENTATION-DATA-TYPE>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ImplementationDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ImplementationDataType)
        self.assertEqual(elem.name, 'dataPtr_T')
        ptr_target_props = elem.sw_data_def_props[0].ptr_target_props
        self.assertEqual(ptr_target_props.target_category, "TYPE_REFERENCE")
        sw_data_def_props = ptr_target_props.sw_data_def_props
        self.assertEqual(str(sw_data_def_props[0].impl_data_type_ref),
                         "/DataTypes/ImplementationTypes/InactiveActive_T")


class TestApplicationPrimitiveDataType(unittest.TestCase):

    def test_read_write_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationPrimitiveDataType("TypeName")
        xml = '''<APPLICATION-PRIMITIVE-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
</APPLICATION-PRIMITIVE-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationPrimitiveDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationPrimitiveDataType)
        self.assertEqual(elem.name, "TypeName")

    def test_read_write_sw_data_def_props(self):
        writer = autosar.xml.Writer()
        sw_data_def_props = ar_element.SwDataDefPropsConditional(compu_method_ref="/CompuMethod/CompuName")
        element = ar_element.ApplicationPrimitiveDataType("TypeName",
                                                          category="VALUE",
                                                          sw_data_def_props=sw_data_def_props)
        xml = '''<APPLICATION-PRIMITIVE-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <CATEGORY>VALUE</CATEGORY>
  <SW-DATA-DEF-PROPS>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <COMPU-METHOD-REF DEST="COMPU-METHOD">/CompuMethod/CompuName</COMPU-METHOD-REF>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </SW-DATA-DEF-PROPS>
</APPLICATION-PRIMITIVE-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationPrimitiveDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationPrimitiveDataType)
        self.assertEqual(elem.name, "TypeName")
        self.assertEqual(elem.category, "VALUE")
        props: ar_element.SwDataDefPropsConditional = elem.sw_data_def_props[0]
        self.assertEqual(str(props.compu_method_ref), "/CompuMethod/CompuName")


class TestApplicationDataTypeRef(unittest.TestCase):

    def test_read_write_application_array_data_type(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationDataTypeRef(
            "/Package/ShortName",
            ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE)
        xml = '''<APPLICATION-DATA-TYPE-REF DEST="APPLICATION-ARRAY-DATA-TYPE">/Package/ShortName</APPLICATION-DATA-TYPE-REF>'''  # noqa E501 pylint: disable=C0301
        self.assertEqual(writer.write_str_elem(element, "APPLICATION-DATA-TYPE-REF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationDataTypeRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationDataTypeRef)
        self.assertEqual(elem.value, "/Package/ShortName")
        self.assertEqual(elem.dest, ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE)

    def test_read_write_application_assoc_map_data_type(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationDataTypeRef(
            "/Package/ShortName",
            ar_enum.IdentifiableSubTypes.APPLICATION_ASSOC_MAP_DATA_TYPE)
        xml = '''<APPLICATION-DATA-TYPE-REF DEST="APPLICATION-ASSOC-MAP-DATA-TYPE">/Package/ShortName</APPLICATION-DATA-TYPE-REF>'''  # noqa E501 pylint: disable=C0301
        self.assertEqual(writer.write_str_elem(element, "APPLICATION-DATA-TYPE-REF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationDataTypeRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationDataTypeRef)
        self.assertEqual(elem.value, "/Package/ShortName")
        self.assertEqual(elem.dest, ar_enum.IdentifiableSubTypes.APPLICATION_ASSOC_MAP_DATA_TYPE)

    def test_read_write_application_composite_data_type(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationDataTypeRef(
            "/Package/ShortName",
            ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_DATA_TYPE)
        xml = '''<APPLICATION-DATA-TYPE-REF DEST="APPLICATION-COMPOSITE-DATA-TYPE">/Package/ShortName</APPLICATION-DATA-TYPE-REF>'''  # noqa E501 pylint: disable=C0301
        self.assertEqual(writer.write_str_elem(element, "APPLICATION-DATA-TYPE-REF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationDataTypeRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationDataTypeRef)
        self.assertEqual(elem.value, "/Package/ShortName")
        self.assertEqual(elem.dest, ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_DATA_TYPE)

    def test_read_write_application_data_type(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationDataTypeRef(
            "/Package/ShortName",
            ar_enum.IdentifiableSubTypes.APPLICATION_DATA_TYPE)
        xml = '''<APPLICATION-DATA-TYPE-REF DEST="APPLICATION-DATA-TYPE">/Package/ShortName</APPLICATION-DATA-TYPE-REF>'''  # noqa E501 pylint: disable=C0301
        self.assertEqual(writer.write_str_elem(element, "APPLICATION-DATA-TYPE-REF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationDataTypeRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationDataTypeRef)
        self.assertEqual(elem.value, "/Package/ShortName")
        self.assertEqual(elem.dest, ar_enum.IdentifiableSubTypes.APPLICATION_DATA_TYPE)

    def test_read_write_application_deferred_data_type(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationDataTypeRef(
            "/Package/ShortName",
            ar_enum.IdentifiableSubTypes.APPLICATION_DEFERRED_DATA_TYPE)
        xml = '''<APPLICATION-DATA-TYPE-REF DEST="APPLICATION-DEFERRED-DATA-TYPE">/Package/ShortName</APPLICATION-DATA-TYPE-REF>'''  # noqa E501 pylint: disable=C0301
        self.assertEqual(writer.write_str_elem(element, "APPLICATION-DATA-TYPE-REF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationDataTypeRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationDataTypeRef)
        self.assertEqual(elem.value, "/Package/ShortName")
        self.assertEqual(elem.dest, ar_enum.IdentifiableSubTypes.APPLICATION_DEFERRED_DATA_TYPE)

    def test_read_write_application_primitive_data_type(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationDataTypeRef(
            "/Package/ShortName",
            ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)
        xml = '''<APPLICATION-DATA-TYPE-REF DEST="APPLICATION-PRIMITIVE-DATA-TYPE">/Package/ShortName</APPLICATION-DATA-TYPE-REF>'''  # noqa E501 pylint: disable=C0301
        self.assertEqual(writer.write_str_elem(element, "APPLICATION-DATA-TYPE-REF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationDataTypeRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationDataTypeRef)
        self.assertEqual(elem.value, "/Package/ShortName")
        self.assertEqual(elem.dest, ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)

    def test_read_write_application_record_data_type(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationDataTypeRef(
            "/Package/ShortName",
            ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE)
        xml = '''<APPLICATION-DATA-TYPE-REF DEST="APPLICATION-RECORD-DATA-TYPE">/Package/ShortName</APPLICATION-DATA-TYPE-REF>'''  # noqa E501 pylint: disable=C0301
        self.assertEqual(writer.write_str_elem(element, "APPLICATION-DATA-TYPE-REF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationDataTypeRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationDataTypeRef)
        self.assertEqual(elem.value, "/Package/ShortName")
        self.assertEqual(elem.dest, ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE)


class TestApplicationArrayElement(unittest.TestCase):

    def test_read_write_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayElement("ElementName")
        xml = '''<ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
</ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayElement = reader.read_str_elem(xml, "ApplicationArrayElement")
        self.assertIsInstance(elem, ar_element.ApplicationArrayElement)
        self.assertEqual(elem.name, "ElementName")

    def test_read_write_sw_data_def_props(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayElement(
            "ElementName",
            category="VALUE",
            sw_data_def_props=ar_element.SwDataDefPropsConditional(compu_method_ref="/CompuMethod/CompuName"))
        xml = '''<ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <CATEGORY>VALUE</CATEGORY>
  <SW-DATA-DEF-PROPS>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <COMPU-METHOD-REF DEST="COMPU-METHOD">/CompuMethod/CompuName</COMPU-METHOD-REF>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </SW-DATA-DEF-PROPS>
</ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayElement = reader.read_str_elem(xml, "ApplicationArrayElement")
        self.assertIsInstance(elem, ar_element.ApplicationArrayElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertEqual(elem.category, "VALUE")
        props: ar_element.SwDataDefPropsConditional = elem.sw_data_def_props[0]
        self.assertEqual(str(props.compu_method_ref), "/CompuMethod/CompuName")

    def test_read_write_type_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayElement(
            "ElementName",
            type_ref=ar_element.ApplicationDataTypeRef("/ApplicationTypes/TypeName",
                                                       ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE))
        xml = '''<ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <TYPE-TREF DEST="APPLICATION-PRIMITIVE-DATA-TYPE">/ApplicationTypes/TypeName</TYPE-TREF>
</ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayElement = reader.read_str_elem(xml, "ApplicationArrayElement")
        self.assertIsInstance(elem, ar_element.ApplicationArrayElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertEqual(elem.type_ref.value, "/ApplicationTypes/TypeName")
        self.assertEqual(elem.type_ref.dest, ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)

    def test_read_write_array_size_handling(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayElement(
            "ElementName",
            array_size_handling=ar_enum.ArraySizeHandling.ALL_INDICES_DIFFERENT_ARRAY_SIZE)
        xml = '''<ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <ARRAY-SIZE-HANDLING>ALL-INDICES-DIFFERENT-ARRAY-SIZE</ARRAY-SIZE-HANDLING>
</ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayElement = reader.read_str_elem(xml, "ApplicationArrayElement")
        self.assertIsInstance(elem, ar_element.ApplicationArrayElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertEqual(elem.array_size_handling, ar_enum.ArraySizeHandling.ALL_INDICES_DIFFERENT_ARRAY_SIZE)

    def test_read_write_array_size_semantics(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayElement(
            "ElementName",
            array_size_semantics=ar_enum.ArraySizeSemantics.FIXED_SIZE)
        xml = '''<ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <ARRAY-SIZE-SEMANTICS>FIXED-SIZE</ARRAY-SIZE-SEMANTICS>
</ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayElement = reader.read_str_elem(xml, "ApplicationArrayElement")
        self.assertIsInstance(elem, ar_element.ApplicationArrayElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertEqual(elem.array_size_semantics, ar_enum.ArraySizeSemantics.FIXED_SIZE)

    def test_read_write_index_data_type_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayElement(
            "ElementName",
            index_data_type_ref="/Package/TypeName")
        xml = '''<ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <INDEX-DATA-TYPE-REF DEST="APPLICATION-PRIMITIVE-DATA-TYPE">/Package/TypeName</INDEX-DATA-TYPE-REF>
</ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayElement = reader.read_str_elem(xml, "ApplicationArrayElement")
        self.assertIsInstance(elem, ar_element.ApplicationArrayElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertEqual(str(elem.index_data_type_ref), "/Package/TypeName")

    def test_read_write_max_number_of_elements(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayElement(
            "ElementName",
            max_number_of_elements=100)
        xml = '''<ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <MAX-NUMBER-OF-ELEMENTS>100</MAX-NUMBER-OF-ELEMENTS>
</ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayElement = reader.read_str_elem(xml, "ApplicationArrayElement")
        self.assertIsInstance(elem, ar_element.ApplicationArrayElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertEqual(elem.max_number_of_elements, 100)


class TestApplicationRecordElement(unittest.TestCase):

    def test_read_write_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationRecordElement("ElementName")
        xml = '''<APPLICATION-RECORD-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
</APPLICATION-RECORD-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationRecordElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationRecordElement)
        self.assertEqual(elem.name, "ElementName")

    def test_read_write_sw_data_def_props(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationRecordElement(
            "ElementName",
            category="VALUE",
            sw_data_def_props=ar_element.SwDataDefPropsConditional(compu_method_ref="/CompuMethod/CompuName"))
        xml = '''<APPLICATION-RECORD-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <CATEGORY>VALUE</CATEGORY>
  <SW-DATA-DEF-PROPS>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <COMPU-METHOD-REF DEST="COMPU-METHOD">/CompuMethod/CompuName</COMPU-METHOD-REF>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </SW-DATA-DEF-PROPS>
</APPLICATION-RECORD-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationRecordElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationRecordElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertEqual(elem.category, "VALUE")
        props: ar_element.SwDataDefPropsConditional = elem.sw_data_def_props[0]
        self.assertEqual(str(props.compu_method_ref), "/CompuMethod/CompuName")

    def test_read_write_type_ref(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationRecordElement(
            "ElementName",
            type_ref=ar_element.ApplicationDataTypeRef("/ApplicationTypes/TypeName",
                                                       ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE))
        xml = '''<APPLICATION-RECORD-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <TYPE-TREF DEST="APPLICATION-PRIMITIVE-DATA-TYPE">/ApplicationTypes/TypeName</TYPE-TREF>
</APPLICATION-RECORD-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationRecordElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationRecordElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertEqual(elem.type_ref.value, "/ApplicationTypes/TypeName")
        self.assertEqual(elem.type_ref.dest, ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)

    def test_read_write_is_optional(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationRecordElement(
            "ElementName",
            is_optional=False)
        xml = '''<APPLICATION-RECORD-ELEMENT>
  <SHORT-NAME>ElementName</SHORT-NAME>
  <IS-OPTIONAL>false</IS-OPTIONAL>
</APPLICATION-RECORD-ELEMENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationRecordElement = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationRecordElement)
        self.assertEqual(elem.name, "ElementName")
        self.assertFalse(elem.is_optional)


class TestApplicationArrayDataType(unittest.TestCase):

    def test_read_write_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayDataType("TypeName")
        xml = '''<APPLICATION-ARRAY-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
</APPLICATION-ARRAY-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationArrayDataType)
        self.assertEqual(elem.name, "TypeName")

    def test_read_write_dynamic_array_size_profile(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayDataType(
            "TypeName",
            dynamic_array_size_profile="Profile")
        xml = '''<APPLICATION-ARRAY-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <DYNAMIC-ARRAY-SIZE-PROFILE>Profile</DYNAMIC-ARRAY-SIZE-PROFILE>
</APPLICATION-ARRAY-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationArrayDataType)
        self.assertEqual(elem.name, "TypeName")
        self.assertEqual(elem.dynamic_array_size_profile, "Profile")

    def test_read_write_element(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayElement(
            "ElementName",
            type_ref=ar_element.ApplicationDataTypeRef("/ApplicationTypes/TypeName",
                                                       ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE),
            max_number_of_elements=8)
        datatype1 = ar_element.ApplicationArrayDataType(
            "TypeName",
            element=element)
        xml = '''<APPLICATION-ARRAY-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <ELEMENT>
    <SHORT-NAME>ElementName</SHORT-NAME>
    <TYPE-TREF DEST="APPLICATION-PRIMITIVE-DATA-TYPE">/ApplicationTypes/TypeName</TYPE-TREF>
    <MAX-NUMBER-OF-ELEMENTS>8</MAX-NUMBER-OF-ELEMENTS>
  </ELEMENT>
</APPLICATION-ARRAY-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(datatype1), xml)
        reader = autosar.xml.Reader()
        datatype2: ar_element.ApplicationArrayDataType = reader.read_str_elem(xml)
        self.assertIsInstance(datatype2, ar_element.ApplicationArrayDataType)
        self.assertEqual(datatype2.name, "TypeName")
        element = datatype2.element
        self.assertEqual(element.name, "ElementName")
        self.assertEqual(element.type_ref.value, "/ApplicationTypes/TypeName")
        self.assertEqual(element.type_ref.dest, ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)
        self.assertEqual(element.max_number_of_elements, 8)

    def test_read_write_sw_data_def_props(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationArrayDataType(
            "TypeName",
            category="ARRAY",
            sw_data_def_props=ar_element.SwDataDefPropsConditional(compu_method_ref="/CompuMethod/CompuName"))
        xml = '''<APPLICATION-ARRAY-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <CATEGORY>ARRAY</CATEGORY>
  <SW-DATA-DEF-PROPS>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <COMPU-METHOD-REF DEST="COMPU-METHOD">/CompuMethod/CompuName</COMPU-METHOD-REF>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </SW-DATA-DEF-PROPS>
</APPLICATION-ARRAY-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationArrayDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationArrayDataType)
        self.assertEqual(elem.name, "TypeName")
        self.assertEqual(elem.category, "ARRAY")
        props: ar_element.SwDataDefPropsConditional = elem.sw_data_def_props[0]
        self.assertEqual(str(props.compu_method_ref), "/CompuMethod/CompuName")


class TestApplicationRecordDataType(unittest.TestCase):

    def test_read_write_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.ApplicationRecordDataType("TypeName")
        xml = '''<APPLICATION-RECORD-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
</APPLICATION-RECORD-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationRecordDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationRecordDataType)
        self.assertEqual(elem.name, "TypeName")

    def test_read_write_elements_directly_defined_using_sw_data_def_props(self):
        writer = autosar.xml.Writer()
        element1 = ar_element.ApplicationRecordElement(
            "Pitch",
            sw_data_def_props=ar_element.SwDataDefPropsConditional(
                compu_method_ref="/DataTypes/CompuMethods/Pitch_T",
                data_constraint_ref="/DataTypes/DataConstrs/Pitch_DataConstr",
                unit_ref="/DataTypes/Units/deg"))
        element2 = ar_element.ApplicationRecordElement(
            "Yaw",
            sw_data_def_props=ar_element.SwDataDefPropsConditional(
                compu_method_ref="/DataTypes/CompuMethods/Yaw_T",
                data_constraint_ref="/DataTypes/DataConstrs/Yaw_DataConstr",
                unit_ref="/DataTypes/Units/deg"))
        datatype = ar_element.ApplicationRecordDataType(
            "TypeName",
            elements=[element1, element2])
        xml = '''<APPLICATION-RECORD-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <ELEMENTS>
    <APPLICATION-RECORD-ELEMENT>
      <SHORT-NAME>Pitch</SHORT-NAME>
      <SW-DATA-DEF-PROPS>
        <SW-DATA-DEF-PROPS-VARIANTS>
          <SW-DATA-DEF-PROPS-CONDITIONAL>
            <COMPU-METHOD-REF DEST="COMPU-METHOD">/DataTypes/CompuMethods/Pitch_T</COMPU-METHOD-REF>
            <DATA-CONSTR-REF DEST="DATA-CONSTR">/DataTypes/DataConstrs/Pitch_DataConstr</DATA-CONSTR-REF>
            <UNIT-REF DEST="UNIT">/DataTypes/Units/deg</UNIT-REF>
          </SW-DATA-DEF-PROPS-CONDITIONAL>
        </SW-DATA-DEF-PROPS-VARIANTS>
      </SW-DATA-DEF-PROPS>
    </APPLICATION-RECORD-ELEMENT>
    <APPLICATION-RECORD-ELEMENT>
      <SHORT-NAME>Yaw</SHORT-NAME>
      <SW-DATA-DEF-PROPS>
        <SW-DATA-DEF-PROPS-VARIANTS>
          <SW-DATA-DEF-PROPS-CONDITIONAL>
            <COMPU-METHOD-REF DEST="COMPU-METHOD">/DataTypes/CompuMethods/Yaw_T</COMPU-METHOD-REF>
            <DATA-CONSTR-REF DEST="DATA-CONSTR">/DataTypes/DataConstrs/Yaw_DataConstr</DATA-CONSTR-REF>
            <UNIT-REF DEST="UNIT">/DataTypes/Units/deg</UNIT-REF>
          </SW-DATA-DEF-PROPS-CONDITIONAL>
        </SW-DATA-DEF-PROPS-VARIANTS>
      </SW-DATA-DEF-PROPS>
    </APPLICATION-RECORD-ELEMENT>
  </ELEMENTS>
</APPLICATION-RECORD-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(datatype), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationRecordDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationRecordDataType)
        self.assertEqual(elem.name, "TypeName")
        self.assertEqual(len(elem.elements), 2)
        child_elem = elem.elements[0]
        self.assertEqual(child_elem.name, "Pitch")
        child_elem = elem.elements[1]
        self.assertEqual(child_elem.name, "Yaw")

    def test_read_write_elements_by_reference(self):
        writer = autosar.xml.Writer()
        element1 = ar_element.ApplicationRecordElement(
            "Pitch",
            category="VALUE",
            type_ref=ar_element.ApplicationDataTypeRef(
                "/DataTypes/Pitch_T",
                ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE))
        element2 = ar_element.ApplicationRecordElement(
            "Yaw",
            category="VALUE",
            type_ref=ar_element.ApplicationDataTypeRef(
                "/DataTypes/Yaw_T",
                ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE))
        datatype = ar_element.ApplicationRecordDataType(
            "TypeName",
            category="STRUCTURE",
            elements=[element1, element2])
        xml = '''<APPLICATION-RECORD-DATA-TYPE>
  <SHORT-NAME>TypeName</SHORT-NAME>
  <CATEGORY>STRUCTURE</CATEGORY>
  <ELEMENTS>
    <APPLICATION-RECORD-ELEMENT>
      <SHORT-NAME>Pitch</SHORT-NAME>
      <CATEGORY>VALUE</CATEGORY>
      <TYPE-TREF DEST="APPLICATION-PRIMITIVE-DATA-TYPE">/DataTypes/Pitch_T</TYPE-TREF>
    </APPLICATION-RECORD-ELEMENT>
    <APPLICATION-RECORD-ELEMENT>
      <SHORT-NAME>Yaw</SHORT-NAME>
      <CATEGORY>VALUE</CATEGORY>
      <TYPE-TREF DEST="APPLICATION-PRIMITIVE-DATA-TYPE">/DataTypes/Yaw_T</TYPE-TREF>
    </APPLICATION-RECORD-ELEMENT>
  </ELEMENTS>
</APPLICATION-RECORD-DATA-TYPE>'''
        self.assertEqual(writer.write_str_elem(datatype), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationRecordDataType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationRecordDataType)
        self.assertEqual(elem.name, "TypeName")
        self.assertEqual(len(elem.elements), 2)
        child_elem = elem.elements[0]
        self.assertEqual(child_elem.name, "Pitch")
        self.assertEqual(str(child_elem.type_ref), "/DataTypes/Pitch_T")
        child_elem = elem.elements[1]
        self.assertEqual(child_elem.name, "Yaw")
        self.assertEqual(str(child_elem.type_ref), "/DataTypes/Yaw_T")


class TestDataTypeMap(unittest.TestCase):
    def test_read_write_appplication_array_data_type_ref(self):
        element = ar_element.DataTypeMap(
            ar_element.ApplicationDataTypeRef("/ApplicationTypes/ShortName",
                                              ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE))
        xml = '''<DATA-TYPE-MAP>
  <APPLICATION-DATA-TYPE-REF DEST="APPLICATION-ARRAY-DATA-TYPE">/ApplicationTypes/ShortName</APPLICATION-DATA-TYPE-REF>
</DATA-TYPE-MAP>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataTypeMap = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataTypeMap)
        self.assertEqual(str(elem.appl_data_type_ref), "/ApplicationTypes/ShortName")
        self.assertEqual(elem.appl_data_type_ref.dest, ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE)

    def test_read_write_primitive_appplication_data_type_ref(self):
        element = ar_element.DataTypeMap(
            ar_element.ApplicationDataTypeRef("/ApplicationTypes/ShortName",
                                              ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE))
        xml = '''<DATA-TYPE-MAP>
  <APPLICATION-DATA-TYPE-REF DEST="APPLICATION-PRIMITIVE-DATA-TYPE">\
/ApplicationTypes/ShortName</APPLICATION-DATA-TYPE-REF>
</DATA-TYPE-MAP>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataTypeMap = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataTypeMap)
        self.assertEqual(str(elem.appl_data_type_ref), "/ApplicationTypes/ShortName")
        self.assertEqual(elem.appl_data_type_ref.dest, ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)

    def test_read_write_implementation_data_type_ref(self):
        element = ar_element.DataTypeMap(
            impl_data_type_ref=ar_element.ImplementationDataTypeRef("/ImplementationTypes/ShortName"))
        xml = '''<DATA-TYPE-MAP>
  <IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">\
/ImplementationTypes/ShortName</IMPLEMENTATION-DATA-TYPE-REF>
</DATA-TYPE-MAP>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataTypeMap = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataTypeMap)
        self.assertEqual(str(elem.impl_data_type_ref), "/ImplementationTypes/ShortName")
        self.assertEqual(elem.impl_data_type_ref.dest, ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)


class TestDataTypeMappingSet(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.DataTypeMappingSet("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<DATA-TYPE-MAPPING-SET>
  <SHORT-NAME>ShortName</SHORT-NAME>
</DATA-TYPE-MAPPING-SET>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataTypeMappingSet = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataTypeMappingSet)

    def test_read_write_data_type_maps(self):
        data_type_map = ar_element.DataTypeMap(
            appl_data_type_ref=ar_element.ApplicationDataTypeRef(
                "/ApplicationTypes/ShortName", ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE),
            impl_data_type_ref=ar_element.ImplementationDataTypeRef("/ImplementationTypes/ShortName"))
        element = ar_element.DataTypeMappingSet("MappingSet", data_type_maps=data_type_map)
        xml = '''<DATA-TYPE-MAPPING-SET>
  <SHORT-NAME>MappingSet</SHORT-NAME>
  <DATA-TYPE-MAPS>
    <DATA-TYPE-MAP>
      <APPLICATION-DATA-TYPE-REF DEST="APPLICATION-PRIMITIVE-DATA-TYPE">\
/ApplicationTypes/ShortName</APPLICATION-DATA-TYPE-REF>
      <IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">\
/ImplementationTypes/ShortName</IMPLEMENTATION-DATA-TYPE-REF>
    </DATA-TYPE-MAP>
  </DATA-TYPE-MAPS>
</DATA-TYPE-MAPPING-SET>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataTypeMappingSet = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataTypeMappingSet)
        self.assertEqual(len(elem.data_type_maps), 1)
        data_type_map = elem.data_type_maps[0]
        self.assertEqual(str(data_type_map.appl_data_type_ref),
                         "/ApplicationTypes/ShortName")
        self.assertEqual(data_type_map.appl_data_type_ref.dest,
                         ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)
        self.assertEqual(str(data_type_map.impl_data_type_ref),
                         "/ImplementationTypes/ShortName")
        self.assertEqual(data_type_map.impl_data_type_ref.dest,
                         ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)


if __name__ == '__main__':
    unittest.main()
