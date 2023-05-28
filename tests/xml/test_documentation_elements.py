"""
Unit tests for documentation-related elements
"""
# pylint: disable=missing-class-docstring, missing-function-docstring, line-too-long
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import unittest
import autosar.xml.enumeration as ar_enum
import autosar.xml.element as ar_element
import autosar


class TestBreak(unittest.TestCase):

    def test_write_element(self):
        element = ar_element.Break()
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), '<BR/>')

    def test_read_element(self):
        xml = '<BR/>'
        reader = autosar.xml.Reader()
        elem: ar_element.Break = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Break)


class TestEmphasisText(unittest.TestCase):

    def test_write_element_default(self):
        writer = autosar.xml.Writer()
        element = ar_element.EmphasisText('Services')
        self.assertEqual(writer.write_str_elem(element),
                         '<E>Services</E>')

    def test_write_element_with_type(self):
        writer = autosar.xml.Writer()
        element = ar_element.EmphasisText('Services',
                                          type=ar_enum.EmphasisType.ITALIC)
        self.assertEqual(writer.write_str_elem(element),
                         '<E TYPE="ITALIC">Services</E>')

    def test_write_element_with_font(self):
        writer = autosar.xml.Writer()
        element = ar_element.EmphasisText('Services',
                                          font=ar_enum.EmphasisFont.MONO)
        self.assertEqual(writer.write_str_elem(element),
                         '<E FONT="MONO">Services</E>')

    def test_write_element_with_type_and_font(self):
        writer = autosar.xml.Writer()
        element = ar_element.EmphasisText('Services',
                                          font=ar_enum.EmphasisFont.MONO,
                                          type=ar_enum.EmphasisType.PLAIN)
        self.assertEqual(writer.write_str_elem(element),
                         '<E FONT="MONO" TYPE="PLAIN">Services</E>')

    def test_write_element_with_color(self):
        writer = autosar.xml.Writer()
        element = ar_element.EmphasisText('Services', color="800000")
        self.assertEqual(writer.write_str_elem(element),
                         '<E COLOR="800000">Services</E>')

    def test_read_element_default(self):
        xml = '<E>Services</E>'
        reader = autosar.xml.Reader()
        elem: ar_element.EmphasisText = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EmphasisText)
        self.assertEqual(elem.elements[0], 'Services')


class TestIndexEntry(unittest.TestCase):

    def test_write_element_default(self):
        writer = autosar.xml.Writer()
        element = ar_element.IndexEntry('Entry')
        self.assertEqual(writer.write_str_elem(element),
                         '<IE>Entry</IE>')

    def test_read_element_default(self):
        xml = '<IE>Entry</IE>'
        reader = autosar.xml.Reader()
        elem: ar_element.IndexEntry = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.IndexEntry)
        self.assertEqual(elem.text, 'Entry')


class TestTechnicalTerm(unittest.TestCase):

    def test_write_element_default(self):
        writer = autosar.xml.Writer()
        element = ar_element.TechnicalTerm('Integrator')
        self.assertEqual(writer.write_str_elem(element),
                         '<TT>Integrator</TT>')

    def test_write_element_with_tex_render(self):
        writer = autosar.xml.Writer()
        element = ar_element.TechnicalTerm('Integrator', tex_render=r'\sep{}')
        self.assertEqual(writer.write_str_elem(element),
                         r'<TT TEX-RENDER="\sep{}">Integrator</TT>')

    def test_write_element_with_type(self):
        writer = autosar.xml.Writer()
        element = ar_element.TechnicalTerm('Distance', type="CALPRM")
        self.assertEqual(writer.write_str_elem(element),
                         '<TT TYPE="CALPRM">Distance</TT>')

    def test_read_element_default(self):
        xml = '<TT>Integrator</TT>'
        reader = autosar.xml.Reader()
        elem: ar_element.TechnicalTerm = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.TechnicalTerm)
        self.assertEqual(elem.text, 'Integrator')

    def test_read_element_with_type(self):
        xml = '<TT TYPE="ROLE">Integrator</TT>'
        reader = autosar.xml.Reader()
        elem: ar_element.TechnicalTerm = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.TechnicalTerm)
        self.assertEqual(elem.text, 'Integrator')
        self.assertEqual(elem.type, 'ROLE')


class TestSubscript(unittest.TestCase):

    def test_write_element_default(self):
        writer = autosar.xml.Writer()
        element = ar_element.Subscript('subscript-text')
        self.assertEqual(writer.write_str_elem(element),
                         '<SUB>subscript-text</SUB>')

    def test_read_element_default(self):
        xml = '<SUB>subscript-text</SUB>'
        reader = autosar.xml.Reader()
        elem: ar_element.Subscript = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Subscript)
        self.assertEqual(elem.text, 'subscript-text')


class TestSuperScript(unittest.TestCase):

    def test_write_element_default(self):
        writer = autosar.xml.Writer()
        element = ar_element.Superscript('superscript-text')
        self.assertEqual(writer.write_str_elem(element),
                         '<SUP>superscript-text</SUP>')

    def test_read_element_default(self):
        reader = autosar.xml.Reader()
        xml = '<SUP>superscript-text</SUP>'
        elem: ar_element.TechnicalTerm = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Superscript)
        self.assertEqual(elem.text, 'superscript-text')


class TestMultilanguageLongName(unittest.TestCase):

    def test_write_element_for_all_simple(self):
        writer = autosar.xml.Writer()
        element = ar_element.MultilanguageLongName(
            (ar_enum.Language.FOR_ALL, 'My Name'))
        self.assertEqual(writer.write_str_elem(element, 'LONG-NAME'), '''<LONG-NAME>
  <L-4 L="FOR-ALL">My Name</L-4>
</LONG-NAME>''')

    def test_write_element_for_all_mixed_content(self):
        writer = autosar.xml.Writer()
        element = ar_element.MultilanguageLongName()
        element.append(ar_element.LanguageLongName(
            ar_enum.Language.FOR_ALL,
            ['Name ',
             ar_element.Subscript(
                 'Subscript text'),
             ' More text ',
             ar_element.TechnicalTerm('Technical Term', type="MY-TYPE")]))
        self.assertEqual(writer.write_str_elem(element, 'LONG-NAME'), '''<LONG-NAME>
  <L-4 L="FOR-ALL">Name <SUB>Subscript text</SUB> More text <TT TYPE="MY-TYPE">Technical Term</TT></L-4>
</LONG-NAME>''')

    def test_read_element_english_simple(self):
        xml = '''
<LONG-NAME>
  <L-4 L="EN">My Name</L-4>'
</LONG-NAME>
'''
        reader = autosar.xml.Reader()
        elem: ar_element.MultilanguageLongName = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.MultilanguageLongName)
        self.assertEqual(elem.elements[0].parts[0], 'My Name')
        self.assertEqual(elem.elements[0].language, ar_enum.Language.EN)


class TestMultiLanguageOverviewParagraph(unittest.TestCase):

    def test_write_element_for_all_simple(self):
        writer = autosar.xml.Writer()
        element = ar_element.MultiLanguageOverviewParagraph(
            (ar_enum.Language.FOR_ALL, 'Description'))
        self.assertEqual(writer.write_str_elem(element, 'DESC'), '''<DESC>
  <L-2 L="FOR-ALL">Description</L-2>
</DESC>''')

    def test_read_element_english_simple(self):
        xml = '''
<DESC>
  <L-2 L="EN">Description</L-2>'
</DESC>
'''
        reader = autosar.xml.Reader()
        elem: ar_element.MultilanguageLongName = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.MultiLanguageOverviewParagraph)
        self.assertEqual(elem.elements[0].parts[0], 'Description')
        self.assertEqual(elem.elements[0].language, ar_enum.Language.EN)

    def test_read_element_chinese_simple(self):
        xml = '''
<DESC>
  <L-2 L="ZH">测试</L-2>'
</DESC>
'''
        reader = autosar.xml.Reader()
        elem: ar_element.MultilanguageLongName = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.MultiLanguageOverviewParagraph)
        self.assertEqual(elem.elements[0].parts[0], '测试')
        self.assertEqual(elem.elements[0].language, ar_enum.Language.ZH)


class TestLanguageParagraph(unittest.TestCase):

    def test_write_for_all_simple_content(self):
        writer = autosar.xml.Writer()
        element = ar_element.LanguageParagraph(
            ar_enum.Language.FOR_ALL, 'Text')
        self.assertEqual(writer.write_str_elem(element),
                         '<L-1 L="FOR-ALL">Text</L-1>')

    def test_read_element_english_simple(self):
        xml = '<L-1 L="EN">Text</L-1>'
        reader = autosar.xml.Reader()
        elem: ar_element.LanguageParagraph = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.LanguageParagraph)
        self.assertEqual(elem.parts[0], 'Text')
        self.assertEqual(elem.language, ar_enum.Language.EN)


class TestMultiLanguageParagraph(unittest.TestCase):

    def test_write_element_for_all_simple(self):
        writer = autosar.xml.Writer()
        element = ar_element.MultiLanguageParagraph(
            (ar_enum.Language.FOR_ALL, 'Text'))
        self.assertEqual(writer.write_str_elem(element), '''<P>
  <L-1 L="FOR-ALL">Text</L-1>
</P>''')

    def test_write_element_with_document_selectable_attr(self):
        writer = autosar.xml.Writer()
        element = ar_element.MultiLanguageParagraph((ar_enum.Language.FOR_ALL, 'Text'),
                                                    semantic_information='SEMANTIC',
                                                    view='MY-VIEW')
        self.assertEqual(writer.write_str_elem(element), '''<P SI="SEMANTIC" VIEW="MY-VIEW">
  <L-1 L="FOR-ALL">Text</L-1>
</P>''')

    def test_write_element_with_paginatable_and_help_entry_attr(self):
        writer = autosar.xml.Writer()
        element = ar_element.MultiLanguageParagraph((ar_enum.Language.FOR_ALL, 'Text'),
                                                    page_break=ar_enum.PageBreak.NO_BREAK,
                                                    keep_with_previous=ar_enum.KeepWithPrevious.KEEP,
                                                    help_entry='MY-HELP-ENTRY')
        self.assertEqual(writer.write_str_elem(element), '''<P BREAK="NO-BREAK" KEEP-WITH-PREVIOUS="KEEP" HELP-ENTRY="MY-HELP-ENTRY">
  <L-1 L="FOR-ALL">Text</L-1>
</P>''')

    def test_read_element_for_all_simple(self):
        xml = '''
<P>
  <L-1 L="FOR-ALL">Text</L-1>'
</P>
'''
        reader = autosar.xml.Reader()
        elem: ar_element.MultiLanguageParagraph = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.MultiLanguageParagraph)
        self.assertEqual(elem.elements[0].parts[0], 'Text')
        self.assertEqual(elem.elements[0].language, ar_enum.Language.FOR_ALL)


class TestLanguageVerbatim(unittest.TestCase):

    def test_write_element_for_all_simple(self):
        writer = autosar.xml.Writer()
        element = ar_element.LanguageVerbatim(
            ar_enum.Language.FOR_ALL, '  Text surrounded by spaces   ')
        self.assertEqual(writer.write_str_elem(
            element), '<L-5 L="FOR-ALL">  Text surrounded by spaces   </L-5>')

    def test_read_element_for_all_simple(self):
        xml = '<L-5 L="FOR-ALL">  Text surrounded by spaces   </L-5>'
        reader = autosar.xml.Reader()
        elem: ar_element.LanguageVerbatim = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.LanguageVerbatim)
        self.assertEqual(elem.parts[0], '  Text surrounded by spaces   ')
        self.assertEqual(elem.language, ar_enum.Language.FOR_ALL)


class TestMultiLanguageVerbatim(unittest.TestCase):

    def test_write_element_for_all_simple(self):
        writer = autosar.xml.Writer()
        element = ar_element.MultiLanguageVerbatim(
            (ar_enum.Language.FOR_ALL, 'Text'))
        self.assertEqual(writer.write_str_elem(element), '''<VERBATIM>
  <L-5 L="FOR-ALL">Text</L-5>
</VERBATIM>''')

    def test_read_element_for_all_simple(self):
        xml = '''
<VERBATIM>
  <L-5 L="FOR-ALL">Text</L-5>'
</VERBATIM>
'''
        reader = autosar.xml.Reader()
        elem: ar_element.MultiLanguageVerbatim = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.MultiLanguageVerbatim)
        self.assertEqual(elem.elements[0].parts[0], 'Text')
        self.assertEqual(elem.elements[0].language, ar_enum.Language.FOR_ALL)


class TestDocumentationBlock(unittest.TestCase):
    def test_write_element_default(self):
        writer = autosar.xml.Writer()
        element = ar_element.DocumentationBlock()
        self.assertEqual(writer.write_str_elem(
            element, 'ANNOTATION-TEXT'), '<ANNOTATION-TEXT/>')

    def test_write_element_with_paragraph(self):
        writer = autosar.xml.Writer()
        element = ar_element.DocumentationBlock()
        element.append(ar_element.MultiLanguageParagraph(
            (ar_enum.Language.EN, 'Paragraph Text')))
        self.assertEqual(writer.write_str_elem(element, 'ANNOTATION-TEXT'), '''<ANNOTATION-TEXT>
  <P>
    <L-1 L="EN">Paragraph Text</L-1>
  </P>
</ANNOTATION-TEXT>''')

    def test_write_element_with_verbatim(self):
        writer = autosar.xml.Writer()
        element = ar_element.DocumentationBlock()
        element.append(ar_element.MultiLanguageVerbatim(
            (ar_enum.Language.EN, 'Verbatim Text')))
        self.assertEqual(writer.write_str_elem(element, 'ANNOTATION-TEXT'), '''<ANNOTATION-TEXT>
  <VERBATIM>
    <L-5 L="EN">Verbatim Text</L-5>
  </VERBATIM>
</ANNOTATION-TEXT>''')

    def test_read_element_default(self):
        xml = '<ANNOTATION-TEXT/>'
        reader = autosar.xml.Reader()
        elem: ar_element.DocumentationBlock = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DocumentationBlock)

    def test_read_element_with_paragraph(self):
        xml = '''
<ANNOTATION-TEXT>
  <P>
    <L-1 L="EN">Paragraph Text</L-1>
  </P>
</ANNOTATION-TEXT>'''
        reader = autosar.xml.Reader()
        elem: ar_element.DocumentationBlock = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DocumentationBlock)
        child_elem = elem.elements[0]
        self.assertIsInstance(child_elem, ar_element.MultiLanguageParagraph)
        self.assertEqual(child_elem.elements[0].parts[0], 'Paragraph Text')
        self.assertEqual(child_elem.elements[0].language, ar_enum.Language.EN)

    def test_read_element_with_verbatim(self):
        xml = '''
<ANNOTATION-TEXT>
  <VERBATIM>
    <L-5 L="EN">Verbatim Text</L-5>
  </VERBATIM>
</ANNOTATION-TEXT>'''
        reader = autosar.xml.Reader()
        elem: ar_element.DocumentationBlock = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DocumentationBlock)
        child_elem = elem.elements[0]
        self.assertIsInstance(child_elem, ar_element.MultiLanguageVerbatim)
        self.assertEqual(child_elem.elements[0].parts[0], 'Verbatim Text')
        self.assertEqual(child_elem.elements[0].language, ar_enum.Language.EN)


class TestAnnotation(unittest.TestCase):
    def test_write_element_default(self):
        writer = autosar.xml.Writer()
        element = ar_element.Annotation()
        self.assertEqual(writer.write_str_elem(element), '<ANNOTATION/>')

    def test_write_element_with_label_and_annotation_text(self):
        writer = autosar.xml.Writer()
        element = ar_element.Annotation()
        element.label = ar_element.MultilanguageLongName(
            (ar_enum.Language.FOR_ALL, 'My Label'))
        paragraph = ar_element.MultiLanguageParagraph(
            (ar_enum.Language.EN, 'Paragraph Text'))
        element.text = ar_element.DocumentationBlock(paragraph)
        self.assertEqual(writer.write_str_elem(element), '''<ANNOTATION>
  <LABEL>
    <L-4 L="FOR-ALL">My Label</L-4>
  </LABEL>
  <ANNOTATION-TEXT>
    <P>
      <L-1 L="EN">Paragraph Text</L-1>
    </P>
  </ANNOTATION-TEXT>
</ANNOTATION>''')

    def test_read_element_default(self):
        xml = '<ANNOTATION/>'
        reader = autosar.xml.Reader()
        elem: ar_element.Annotation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Annotation)

    def test_read_element_with_label_and_annotation_text(self):
        xml = '''
<ANNOTATION>
  <LABEL>
    <L-4 L="FOR-ALL">My Label</L-4>
  </LABEL>
  <ANNOTATION-TEXT>
    <P>
      <L-1 L="EN">Paragraph Text</L-1>
    </P>
  </ANNOTATION-TEXT>
</ANNOTATION>
'''
        reader = autosar.xml.Reader()
        elem: ar_element.Annotation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Annotation)
        annotation_label: ar_element.MultilanguageLongName = elem.label
        self.assertIsInstance(
            annotation_label, ar_element.MultilanguageLongName)
        self.assertEqual(annotation_label.elements[0].parts[0], "My Label")
        annotation_text: ar_element.DocumentationBlock = elem.text
        self.assertIsInstance(annotation_text, ar_element.DocumentationBlock)
        self.assertEqual(
            annotation_text.elements[0].elements[0].parts[0], "Paragraph Text")


if __name__ == '__main__':
    unittest.main()
