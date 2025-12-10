"""Unit tests for common structure elements"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import datetime
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402


class TestSpecialDataGroup(unittest.TestCase):

    def test_empty(self):
        element = ar_element.SpecialDataGroup()
        xml = '<SDG/>'
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)

    def test_gid(self):
        element = ar_element.SpecialDataGroup(gid="MyGID")
        xml = '<SDG GID="MyGID"/>'
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)
        self.assertEqual(elem.gid, "MyGID")

    def test_caption(self):
        element = ar_element.SpecialDataGroup(caption="MyCaption")
        xml = '''<SDG>
  <SDG-CAPTION>MyCaption</SDG-CAPTION>
</SDG>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)
        self.assertEqual(elem.caption, "MyCaption")

    def test_content_from_string(self):
        element = ar_element.SpecialDataGroup(content="MyContent")
        xml = '''<SDG>
  <SD>MyContent</SD>
</SDG>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)
        self.assertEqual(len(elem.content), 1)
        child: ar_element.SpecialDataElement = elem.content[0]
        self.assertEqual(child.text, "MyContent")
        self.assertIsNone(child.gid)

    def test_content_from_tuple(self):
        element = ar_element.SpecialDataGroup(content=("MyGID", "MyContent"))
        xml = '''<SDG>
  <SD GID="MyGID">MyContent</SD>
</SDG>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)
        self.assertEqual(len(elem.content), 1)
        child: ar_element.SpecialDataElement = elem.content[0]
        self.assertEqual(child, ar_element.SpecialDataElement("MyContent", "MyGID"))

    def test_content_from_named_tuple(self):
        element = ar_element.SpecialDataGroup(content=ar_element.SpecialDataElement("MyContent", "MyGID", ))
        xml = '''<SDG>
  <SD GID="MyGID">MyContent</SD>
</SDG>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)
        self.assertEqual(len(elem.content), 1)
        child: ar_element.SpecialDataElement = elem.content[0]
        self.assertEqual(child, ar_element.SpecialDataElement("MyContent", "MyGID"))

    def test_content_from_int(self):
        element = ar_element.SpecialDataGroup(content=100)
        xml = '''<SDG>
  <SDF>100</SDF>
</SDG>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)
        self.assertEqual(len(elem.content), 1)
        child: ar_element.SpecialDataValue = elem.content[0]
        self.assertEqual(child, ar_element.SpecialDataValue(100))

    def test_content_from_float(self):
        element = ar_element.SpecialDataGroup(content=0.5)
        xml = '''<SDG>
  <SDF>0.5</SDF>
</SDG>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)
        self.assertEqual(len(elem.content), 1)
        child: ar_element.SpecialDataValue = elem.content[0]
        self.assertEqual(child, ar_element.SpecialDataValue(0.5))

    def test_content_from_list(self):
        element = ar_element.SpecialDataGroup(gid="MyGID0",
                                              content=["MyContent1",
                                                       ("MyGID2", "MyContent2"),
                                                       ar_element.SpecialDataElement("MyContent3"),
                                                       ar_element.SpecialDataElement("MyContent4", "MyGID4"),
                                                       "true",
                                                       50,
                                                       ("MyGID6", 0.125)])
        xml = '''<SDG GID="MyGID0">
  <SD>MyContent1</SD>
  <SD GID="MyGID2">MyContent2</SD>
  <SD>MyContent3</SD>
  <SD GID="MyGID4">MyContent4</SD>
  <SD>true</SD>
  <SDF>50</SDF>
  <SDF GID="MyGID6">0.125</SDF>
</SDG>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)
        self.assertEqual(len(elem.content), 7)
        child: ar_element.SpecialDataElement = elem.content[0]
        self.assertEqual(child, ar_element.SpecialDataElement("MyContent1"))
        child = elem.content[1]
        self.assertEqual(child, ar_element.SpecialDataElement("MyContent2", "MyGID2"))
        child = elem.content[2]
        self.assertEqual(child, ar_element.SpecialDataElement("MyContent3"))
        child = elem.content[3]
        self.assertEqual(child, ar_element.SpecialDataElement("MyContent4", "MyGID4"))
        child = elem.content[4]
        self.assertEqual(child, ar_element.SpecialDataElement("true"))
        child2: ar_element.SpecialDataValue = elem.content[5]
        self.assertEqual(child2, ar_element.SpecialDataValue(50))
        child2 = elem.content[6]
        self.assertEqual(child2, ar_element.SpecialDataValue(0.125, "MyGID6"))

    def test_nested_content_string(self):
        element = ar_element.SpecialDataGroup(gid="OuterGID", content={"gid": "InnerGID", "content": "InnerContent"})
        xml = '''<SDG GID="OuterGID">
  <SDG GID="InnerGID">
    <SD>InnerContent</SD>
  </SDG>
</SDG>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SpecialDataGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SpecialDataGroup)
        self.assertEqual(elem.gid, "OuterGID")
        self.assertEqual(len(elem.content), 1)
        child: ar_element.SpecialDataGroup = elem.content[0]
        self.assertEqual(child.gid, "InnerGID")
        self.assertEqual(len(child.content), 1)
        grand_child: ar_element.SpecialDataElement = child.content[0]
        self.assertEqual(grand_child, ar_element.SpecialDataElement("InnerContent"))


class TestModification(unittest.TestCase):

    def test_empty(self):
        element = ar_element.Modification()
        xml = '<MODIFICATION/>'
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.Modification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Modification)

    def test_change(self):
        change = ar_element.MultiLanguageOverviewParagraph((ar_enum.Language.FOR_ALL, 'MyChange'))
        element = ar_element.Modification(change=change)
        xml = '''<MODIFICATION>
  <CHANGE>
    <L-2 L="FOR-ALL">MyChange</L-2>
  </CHANGE>
</MODIFICATION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.Modification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Modification)
        self.assertIsInstance(elem.change, ar_element.MultiLanguageOverviewParagraph)
        self.assertEqual(str(elem.change.elements[0].parts[0]), "MyChange")

    def test_reason(self):
        reason = ar_element.MultiLanguageOverviewParagraph((ar_enum.Language.FOR_ALL, 'MyReason'))
        element = ar_element.Modification(reason=reason)
        xml = '''<MODIFICATION>
  <REASON>
    <L-2 L="FOR-ALL">MyReason</L-2>
  </REASON>
</MODIFICATION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.Modification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Modification)
        self.assertIsInstance(elem.reason, ar_element.MultiLanguageOverviewParagraph)
        self.assertEqual(str(elem.reason.elements[0].parts[0]), "MyReason")


class TestDocRevision(unittest.TestCase):

    def test_empty(self):
        element = ar_element.DocRevision()
        xml = '<DOC-REVISION/>'
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DocRevision)

    def test_revision_label(self):
        revision = "1.2.3"
        element = ar_element.DocRevision(revision_label=revision)
        xml = f'''<DOC-REVISION>
  <REVISION-LABEL>{revision}</REVISION-LABEL>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(elem.revision_label.value, revision)

    def test_revision_label_p1(self):
        revision = "1.2.3"
        element = ar_element.DocRevision(revision_label_p1=revision)
        xml = f'''<DOC-REVISION>
  <REVISION-LABEL-P1>{revision}</REVISION-LABEL-P1>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(elem.revision_label_p1.value, revision)

    def test_revision_label_p2(self):
        revision = "1.2.3"
        element = ar_element.DocRevision(revision_label_p2=revision)
        xml = f'''<DOC-REVISION>
  <REVISION-LABEL-P2>{revision}</REVISION-LABEL-P2>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(elem.revision_label_p2.value, revision)

    def test_state(self):
        state = "MyState"
        element = ar_element.DocRevision(state=state)
        xml = f'''<DOC-REVISION>
  <STATE>{state}</STATE>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(elem.state, state)

    def test_issued_by(self):
        issuer = "MyName"
        element = ar_element.DocRevision(issued_by=issuer)
        xml = f'''<DOC-REVISION>
  <ISSUED-BY>{issuer}</ISSUED-BY>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(elem.issued_by, issuer)

    def test_date_from_str(self):
        date = "2025-01-01"
        element = ar_element.DocRevision(date=date)
        xml = f'''<DOC-REVISION>
  <DATE>{date}</DATE>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(elem.date.value.year, 2025)
        self.assertEqual(elem.date.value.month, 1)
        self.assertEqual(elem.date.value.day, 1)
        self.assertEqual(str(elem.date), date)

    def test_datetime_from_str(self):
        date = "2025-01-02T12:34:56+02:00"
        element = ar_element.DocRevision(date=date)
        xml = f'''<DOC-REVISION>
  <DATE>{date}</DATE>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(elem.date.value.year, 2025)
        self.assertEqual(elem.date.value.month, 1)
        self.assertEqual(elem.date.value.day, 2)
        self.assertEqual(elem.date.value.hour, 12)
        self.assertEqual(elem.date.value.minute, 34)
        self.assertEqual(elem.date.value.second, 56)
        self.assertEqual(str(elem.date), date)

    def test_date_from_date(self):
        date = datetime.date(2025, 1, 2)
        element = ar_element.DocRevision(date=date)
        xml = f'''<DOC-REVISION>
  <DATE>{date.isoformat()}</DATE>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(elem.date.value.year, 2025)
        self.assertEqual(elem.date.value.month, 1)
        self.assertEqual(elem.date.value.day, 2)
        self.assertEqual(str(elem.date), date.isoformat())

    def test_date_from_datetime(self):
        tz = datetime.timezone(datetime.timedelta(hours=2))
        date = datetime.datetime(year=2025, month=1, day=2,
                                 hour=12, minute=34, second=56,
                                 tzinfo=tz)
        element = ar_element.DocRevision(date=date)
        xml = f'''<DOC-REVISION>
  <DATE>{date.isoformat()}</DATE>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(elem.date.value.year, 2025)
        self.assertEqual(elem.date.value.month, 1)
        self.assertEqual(elem.date.value.day, 2)
        self.assertEqual(elem.date.value.hour, 12)
        self.assertEqual(elem.date.value.minute, 34)
        self.assertEqual(elem.date.value.second, 56)
        self.assertEqual(str(elem.date), date.isoformat())

    def test_modifications_from_single_element(self):
        change = ar_enum.Language.FOR_ALL, "Made some changes"
        element = ar_element.DocRevision(modifications=change)
        xml = f'''<DOC-REVISION>
  <MODIFICATIONS>
    <MODIFICATION>
      <CHANGE>
        <L-2 L="FOR-ALL">{change[1]}</L-2>
      </CHANGE>
    </MODIFICATION>
  </MODIFICATIONS>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(len(elem.modifications), 1)
        modification: ar_element.Modification = elem.modifications[0]
        self.assertEqual(modification.change.elements[0].language, change[0])
        self.assertEqual(modification.change.elements[0].parts[0], change[1])

    def test_modifications_from_list_of_elements(self):
        changes = [(ar_enum.Language.FOR_ALL, "First Change"),
                   ar_element.Modification(change=(ar_enum.Language.FOR_ALL, "Second Change"),
                                           reason=(ar_enum.Language.FOR_ALL, "Reason for second change"))]
        element = ar_element.DocRevision(modifications=changes)
        xml = '''<DOC-REVISION>
  <MODIFICATIONS>
    <MODIFICATION>
      <CHANGE>
        <L-2 L="FOR-ALL">First Change</L-2>
      </CHANGE>
    </MODIFICATION>
    <MODIFICATION>
      <CHANGE>
        <L-2 L="FOR-ALL">Second Change</L-2>
      </CHANGE>
      <REASON>
        <L-2 L="FOR-ALL">Reason for second change</L-2>
      </REASON>
    </MODIFICATION>
  </MODIFICATIONS>
</DOC-REVISION>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DocRevision = reader.read_str_elem(xml)
        self.assertEqual(len(elem.modifications), 2)
        modification: ar_element.Modification = elem.modifications[0]
        self.assertEqual(modification.change.elements[0].language, changes[0][0])
        self.assertEqual(modification.change.elements[0].parts[0], changes[0][1])
        modification = elem.modifications[1]
        self.assertEqual(modification.change.elements[0].language, changes[1].change.elements[0].language)
        self.assertEqual(modification.change.elements[0].parts[0], changes[1].change.elements[0].parts[0])
        self.assertEqual(modification.reason.elements[0].language, changes[1].reason.elements[0].language)
        self.assertEqual(modification.reason.elements[0].parts[0], changes[1].reason.elements[0].parts[0])


class TestAdminData(unittest.TestCase):

    def test_empty(self):
        element = ar_element.AdminData()
        xml = '<ADMIN-DATA/>'
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AdminData = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AdminData)

    def test_language(self):
        language = ar_enum.Language.EN
        element = ar_element.AdminData(language=language)
        xml = '''<ADMIN-DATA>
  <LANGUAGE>EN</LANGUAGE>
</ADMIN-DATA>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AdminData = reader.read_str_elem(xml)
        self.assertEqual(elem.language, language)

    def test_used_language_from_multi_language_plain_text(self):
        used_languages = ar_element.MultiLanguagePlainText()
        used_languages.append((ar_enum.Language.FR, ""))
        used_languages.append((ar_enum.Language.EN, ""))
        element = ar_element.AdminData(used_languages=used_languages)
        xml = '''<ADMIN-DATA>
  <USED-LANGUAGES>
    <L-10 L="FR"/>
    <L-10 L="EN"/>
  </USED-LANGUAGES>
</ADMIN-DATA>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AdminData = reader.read_str_elem(xml)
        self.assertEqual(len(elem.used_languages.elements), 2)
        child = elem.used_languages.elements[0]
        self.assertEqual(child.language, ar_enum.Language.FR)
        child = elem.used_languages.elements[1]
        self.assertEqual(child.language, ar_enum.Language.EN)

    def test_used_languages_from_tuple_list(self):
        used_languages = [(ar_enum.Language.FR, "Text1"),
                          (ar_enum.Language.EN, "Text2")]
        element = ar_element.AdminData(used_languages=used_languages)
        xml = '''<ADMIN-DATA>
  <USED-LANGUAGES>
    <L-10 L="FR">Text1</L-10>
    <L-10 L="EN">Text2</L-10>
  </USED-LANGUAGES>
</ADMIN-DATA>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AdminData = reader.read_str_elem(xml)
        self.assertEqual(len(elem.used_languages.elements), 2)
        child = elem.used_languages.elements[0]
        self.assertEqual(child.language, ar_enum.Language.FR)
        self.assertEqual(child.text, "Text1")
        child = elem.used_languages.elements[1]
        self.assertEqual(child.language, ar_enum.Language.EN)
        self.assertEqual(child.text, "Text2")

    def test_used_languages_from_enum_list(self):
        used_languages = [ar_enum.Language.FR, ar_enum.Language.EN, ar_enum.Language.DE]
        element = ar_element.AdminData(used_languages=used_languages)
        xml = '''<ADMIN-DATA>
  <USED-LANGUAGES>
    <L-10 L="FR"/>
    <L-10 L="EN"/>
    <L-10 L="DE"/>
  </USED-LANGUAGES>
</ADMIN-DATA>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AdminData = reader.read_str_elem(xml)
        self.assertEqual(len(elem.used_languages.elements), 3)
        child = elem.used_languages.elements[0]
        self.assertEqual(child.language, ar_enum.Language.FR)
        child = elem.used_languages.elements[1]
        self.assertEqual(child.language, ar_enum.Language.EN)
        child = elem.used_languages.elements[2]
        self.assertEqual(child.language, ar_enum.Language.DE)

    def test_doc_revisions_from_single_element(self):
        modifications = [ar_element.Modification((ar_enum.Language.EN, "My Change 1"))]
        doc_revision = ar_element.DocRevision(modifications=modifications)
        element = ar_element.AdminData(doc_revisions=doc_revision)
        xml = '''<ADMIN-DATA>
  <DOC-REVISIONS>
    <DOC-REVISION>
      <MODIFICATIONS>
        <MODIFICATION>
          <CHANGE>
            <L-2 L="EN">My Change 1</L-2>
          </CHANGE>
        </MODIFICATION>
      </MODIFICATIONS>
    </DOC-REVISION>
  </DOC-REVISIONS>
</ADMIN-DATA>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AdminData = reader.read_str_elem(xml)
        self.assertEqual(len(elem.doc_revisions), 1)
        child = elem.doc_revisions[0]
        self.assertEqual(child.modifications[0].change.elements[0].parts[0], "My Change 1")

    def test_doc_revisions_from_list(self):
        revision1 = ar_element.DocRevision(date="2019-12-22")
        revision2 = ar_element.DocRevision(date="2020-02-16")
        revision3 = ar_element.DocRevision(date="2020-04-06")
        element = ar_element.AdminData(doc_revisions=[revision1, revision2, revision3])
        xml = '''<ADMIN-DATA>
  <DOC-REVISIONS>
    <DOC-REVISION>
      <DATE>2019-12-22</DATE>
    </DOC-REVISION>
    <DOC-REVISION>
      <DATE>2020-02-16</DATE>
    </DOC-REVISION>
    <DOC-REVISION>
      <DATE>2020-04-06</DATE>
    </DOC-REVISION>
  </DOC-REVISIONS>
</ADMIN-DATA>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AdminData = reader.read_str_elem(xml)
        self.assertEqual(len(elem.doc_revisions), 3)
        child = elem.doc_revisions[0]
        self.assertEqual(child.date.value.isoformat(), "2019-12-22")
        child = elem.doc_revisions[1]
        self.assertEqual(child.date.value.isoformat(), "2020-02-16")
        child = elem.doc_revisions[2]
        self.assertEqual(child.date.value.isoformat(), "2020-04-06")

    def test_sdgs_from_single_element(self):
        sdg = ar_element.SpecialDataGroup("Outer", content=("Inner", "MyContent"))
        element = ar_element.AdminData(sdgs=sdg)
        xml = '''<ADMIN-DATA>
  <SDGS>
    <SDG GID="Outer">
      <SD GID="Inner">MyContent</SD>
    </SDG>
  </SDGS>
</ADMIN-DATA>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AdminData = reader.read_str_elem(xml)
        self.assertEqual(len(elem.sdgs), 1)
        child = elem.sdgs[0]
        self.assertEqual(child.gid, "Outer")
        self.assertEqual(child.content[0], ar_element.SpecialDataElement("MyContent", "Inner"))

    def test_sdgs_from_list(self):
        sdg1 = ar_element.SpecialDataGroup("Outer1", ("Inner1", "MyContent1"))
        sdg2 = ar_element.SpecialDataGroup("Outer2", ("Inner2", 2))
        element = ar_element.AdminData(sdgs=[sdg1, sdg2])
        xml = '''<ADMIN-DATA>
  <SDGS>
    <SDG GID="Outer1">
      <SD GID="Inner1">MyContent1</SD>
    </SDG>
    <SDG GID="Outer2">
      <SDF GID="Inner2">2</SDF>
    </SDG>
  </SDGS>
</ADMIN-DATA>'''
        writer = autosar.xml.Writer()
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AdminData = reader.read_str_elem(xml)
        self.assertEqual(len(elem.sdgs), 2)
        child = elem.sdgs[0]
        self.assertEqual(child.gid, "Outer1")
        self.assertEqual(child.content[0], ar_element.SpecialDataElement("MyContent1", "Inner1"))
        child = elem.sdgs[1]
        self.assertEqual(child.gid, "Outer2")
        self.assertEqual(child.content[0], ar_element.SpecialDataValue(2, "Inner2"))


if __name__ == '__main__':
    unittest.main()
