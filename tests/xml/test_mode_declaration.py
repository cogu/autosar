"""Unit tests for mode declarations"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.element as ar_element  # noqa E402
import autosar.xml.enumeration as ar_enum  # noqa E402
import autosar  # noqa E402


class TestModeDeclaration(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ModeDeclaration("ModeName")
        writer = autosar.xml.Writer()
        xml = '''<MODE-DECLARATION>
  <SHORT-NAME>ModeName</SHORT-NAME>
</MODE-DECLARATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclaration = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclaration)
        self.assertEqual(elem.name, "ModeName")

    def test_value(self):
        element = ar_element.ModeDeclaration("ModeName", value=0)
        writer = autosar.xml.Writer()
        xml = '''<MODE-DECLARATION>
  <SHORT-NAME>ModeName</SHORT-NAME>
  <VALUE>0</VALUE>
</MODE-DECLARATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclaration = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclaration)
        self.assertEqual(elem.value, 0)


class TestModeErrorBehavior(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ModeErrorBehavior()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element, "MODE-MANAGER-ERROR-BEHAVIOR")
        self.assertEqual(xml, '<MODE-MANAGER-ERROR-BEHAVIOR/>')
        reader = autosar.xml.Reader()
        elem: ar_element.InvalidationPolicy = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeErrorBehavior)

    def test_default_mode_ref(self):
        element = ar_element.ModeErrorBehavior(default_mode_ref="/ModeDeclarations/DeclarationGroupName/ModeName")
        writer = autosar.xml.Writer()
        xml = '''<MODE-MANAGER-ERROR-BEHAVIOR>
  <DEFAULT-MODE-REF DEST="MODE-DECLARATION">/ModeDeclarations/DeclarationGroupName/ModeName</DEFAULT-MODE-REF>
</MODE-MANAGER-ERROR-BEHAVIOR>'''
        self.assertEqual(writer.write_str_elem(element, "MODE-MANAGER-ERROR-BEHAVIOR"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeErrorBehavior = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeErrorBehavior)
        self.assertEqual(str(elem.default_mode_ref), "/ModeDeclarations/DeclarationGroupName/ModeName")

    def test_error_reaction_policy(self):
        element = ar_element.ModeErrorBehavior(error_reaction_policy=ar_enum.ModeErrorReactionPolicy.LAST_MODE)
        writer = autosar.xml.Writer()
        xml = '''<MODE-MANAGER-ERROR-BEHAVIOR>
  <ERROR-REACTION-POLICY>LAST-MODE</ERROR-REACTION-POLICY>
</MODE-MANAGER-ERROR-BEHAVIOR>'''
        self.assertEqual(writer.write_str_elem(element, "MODE-MANAGER-ERROR-BEHAVIOR"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeErrorBehavior = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeErrorBehavior)
        self.assertEqual(elem.error_reaction_policy, ar_enum.ModeErrorReactionPolicy.LAST_MODE)


class TestModeTransition(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ModeTransition("TransitionName")
        writer = autosar.xml.Writer()
        xml = '''<MODE-TRANSITION>
  <SHORT-NAME>TransitionName</SHORT-NAME>
</MODE-TRANSITION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclaration = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeTransition)
        self.assertEqual(elem.name, "TransitionName")

    def test_entered_mode_ref(self):
        element = ar_element.ModeTransition("TransitionName",
                                            entered_mode_ref="/ModeDeclarations/DeclarationGroupName/ModeName")
        writer = autosar.xml.Writer()
        xml = '''<MODE-TRANSITION>
  <SHORT-NAME>TransitionName</SHORT-NAME>
  <ENTERED-MODE-REF DEST="MODE-DECLARATION">/ModeDeclarations/DeclarationGroupName/ModeName</ENTERED-MODE-REF>
</MODE-TRANSITION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclaration = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeTransition)
        self.assertEqual(str(elem.entered_mode_ref), "/ModeDeclarations/DeclarationGroupName/ModeName")

    def test_exited_mode_ref(self):
        element = ar_element.ModeTransition("TransitionName",
                                            exited_mode_ref="/ModeDeclarations/DeclarationGroupName/ModeName")
        writer = autosar.xml.Writer()
        xml = '''<MODE-TRANSITION>
  <SHORT-NAME>TransitionName</SHORT-NAME>
  <EXITED-MODE-REF DEST="MODE-DECLARATION">/ModeDeclarations/DeclarationGroupName/ModeName</EXITED-MODE-REF>
</MODE-TRANSITION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclaration = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeTransition)
        self.assertEqual(str(elem.exited_mode_ref), "/ModeDeclarations/DeclarationGroupName/ModeName")


class TestModeDeclarationGroup(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ModeDeclarationGroup("DeclarationGroupName")
        writer = autosar.xml.Writer()
        xml = '''<MODE-DECLARATION-GROUP>
  <SHORT-NAME>DeclarationGroupName</SHORT-NAME>
</MODE-DECLARATION-GROUP>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroup)
        self.assertEqual(elem.name, "DeclarationGroupName")

    def test_initial_mode_ref(self):
        mode_declaration_ref = "/ModeDeclarations/DeclarationGroupName/ModeName"
        element = ar_element.ModeDeclarationGroup("DeclarationGroupName",
                                                  initial_mode_ref=mode_declaration_ref)
        writer = autosar.xml.Writer()
        xml = f'''<MODE-DECLARATION-GROUP>
  <SHORT-NAME>DeclarationGroupName</SHORT-NAME>
  <INITIAL-MODE-REF DEST="MODE-DECLARATION">{mode_declaration_ref}</INITIAL-MODE-REF>
</MODE-DECLARATION-GROUP>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroup)
        self.assertEqual(str(elem.initial_mode_ref), mode_declaration_ref)

    def test_mode_declarations_by_object(self):
        mode_declarations = [ar_element.ModeDeclaration("OFF", 0),
                             ar_element.ModeDeclaration("ON", 1)]
        element = ar_element.ModeDeclarationGroup("DeclarationGroupName", mode_declarations=mode_declarations)
        writer = autosar.xml.Writer()
        xml = '''<MODE-DECLARATION-GROUP>
  <SHORT-NAME>DeclarationGroupName</SHORT-NAME>
  <MODE-DECLARATIONS>
    <MODE-DECLARATION>
      <SHORT-NAME>OFF</SHORT-NAME>
      <VALUE>0</VALUE>
    </MODE-DECLARATION>
    <MODE-DECLARATION>
      <SHORT-NAME>ON</SHORT-NAME>
      <VALUE>1</VALUE>
    </MODE-DECLARATION>
  </MODE-DECLARATIONS>
</MODE-DECLARATION-GROUP>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroup)
        self.assertEqual(len(elem.mode_declarations), 2)
        mode_declaration = elem.mode_declarations[0]
        self.assertEqual(mode_declaration.name, "OFF")
        self.assertEqual(mode_declaration.value, 0)
        mode_declaration = elem.mode_declarations[1]
        self.assertEqual(mode_declaration.name, "ON")
        self.assertEqual(mode_declaration.value, 1)

    def test_mode_declarations_by_str_list(self):
        mode_declarations = ["OFF", "ON"]
        element = ar_element.ModeDeclarationGroup("DeclarationGroupName", mode_declarations=mode_declarations)
        writer = autosar.xml.Writer()
        xml = '''<MODE-DECLARATION-GROUP>
  <SHORT-NAME>DeclarationGroupName</SHORT-NAME>
  <MODE-DECLARATIONS>
    <MODE-DECLARATION>
      <SHORT-NAME>OFF</SHORT-NAME>
    </MODE-DECLARATION>
    <MODE-DECLARATION>
      <SHORT-NAME>ON</SHORT-NAME>
    </MODE-DECLARATION>
  </MODE-DECLARATIONS>
</MODE-DECLARATION-GROUP>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroup)
        self.assertEqual(len(elem.mode_declarations), 2)
        mode_declaration = elem.mode_declarations[0]
        self.assertEqual(mode_declaration.name, "OFF")
        mode_declaration = elem.mode_declarations[1]
        self.assertEqual(mode_declaration.name, "ON")

    def test_mode_declarations_by_tuple_list(self):
        mode_declarations = [("OFF", 0), ("ON", 1)]
        element = ar_element.ModeDeclarationGroup("DeclarationGroupName", mode_declarations=mode_declarations)
        writer = autosar.xml.Writer()
        xml = '''<MODE-DECLARATION-GROUP>
  <SHORT-NAME>DeclarationGroupName</SHORT-NAME>
  <MODE-DECLARATIONS>
    <MODE-DECLARATION>
      <SHORT-NAME>OFF</SHORT-NAME>
      <VALUE>0</VALUE>
    </MODE-DECLARATION>
    <MODE-DECLARATION>
      <SHORT-NAME>ON</SHORT-NAME>
      <VALUE>1</VALUE>
    </MODE-DECLARATION>
  </MODE-DECLARATIONS>
</MODE-DECLARATION-GROUP>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroup)
        self.assertEqual(len(elem.mode_declarations), 2)
        mode_declaration = elem.mode_declarations[0]
        self.assertEqual(mode_declaration.name, "OFF")
        self.assertEqual(mode_declaration.value, 0)
        mode_declaration = elem.mode_declarations[1]
        self.assertEqual(mode_declaration.name, "ON")
        self.assertEqual(mode_declaration.value, 1)

    def test_mode_manager_error_behavior(self):
        mode_declaration_ref = "/ModeDeclarations/DeclarationGroupName/ModeName"
        mode_error_behavior = ar_element.ModeErrorBehavior(mode_declaration_ref)
        element = ar_element.ModeDeclarationGroup("DeclarationGroupName",
                                                  mode_manager_error_behavior=mode_error_behavior)
        writer = autosar.xml.Writer()
        xml = f'''<MODE-DECLARATION-GROUP>
  <SHORT-NAME>DeclarationGroupName</SHORT-NAME>
  <MODE-MANAGER-ERROR-BEHAVIOR>
    <DEFAULT-MODE-REF DEST="MODE-DECLARATION">{mode_declaration_ref}</DEFAULT-MODE-REF>
  </MODE-MANAGER-ERROR-BEHAVIOR>
</MODE-DECLARATION-GROUP>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroup)
        self.assertIsInstance(elem.mode_manager_error_behavior, ar_element.ModeErrorBehavior)
        self.assertEqual(str(elem.mode_manager_error_behavior.default_mode_ref), mode_declaration_ref)

    def test_mode_user_error_behavior(self):
        mode_declaration_ref = "/ModeDeclarations/DeclarationGroupName/ModeName"
        mode_error_behavior = ar_element.ModeErrorBehavior(mode_declaration_ref)
        element = ar_element.ModeDeclarationGroup("DeclarationGroupName",
                                                  mode_user_error_behavior=mode_error_behavior)
        writer = autosar.xml.Writer()
        xml = f'''<MODE-DECLARATION-GROUP>
  <SHORT-NAME>DeclarationGroupName</SHORT-NAME>
  <MODE-USER-ERROR-BEHAVIOR>
    <DEFAULT-MODE-REF DEST="MODE-DECLARATION">{mode_declaration_ref}</DEFAULT-MODE-REF>
  </MODE-USER-ERROR-BEHAVIOR>
</MODE-DECLARATION-GROUP>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroup)
        self.assertIsInstance(elem.mode_user_error_behavior, ar_element.ModeErrorBehavior)
        self.assertEqual(str(elem.mode_user_error_behavior.default_mode_ref), mode_declaration_ref)

    def test_mode_transitions(self):
        entered_mode_ref = "/ModeDeclarations/DeclarationGroupName/Enter"
        exited_mode_ref = "/ModeDeclarations/DeclarationGroupName/Exit"
        mode_transition = ar_element.ModeTransition("Transition",
                                                    entered_mode_ref,
                                                    exited_mode_ref)
        element = ar_element.ModeDeclarationGroup("DeclarationGroupName", mode_transitions=mode_transition)
        writer = autosar.xml.Writer()
        xml = f'''<MODE-DECLARATION-GROUP>
  <SHORT-NAME>DeclarationGroupName</SHORT-NAME>
  <MODE-TRANSITIONS>
    <MODE-TRANSITION>
      <SHORT-NAME>Transition</SHORT-NAME>
      <ENTERED-MODE-REF DEST="MODE-DECLARATION">{entered_mode_ref}</ENTERED-MODE-REF>
      <EXITED-MODE-REF DEST="MODE-DECLARATION">{exited_mode_ref}</EXITED-MODE-REF>
    </MODE-TRANSITION>
  </MODE-TRANSITIONS>
</MODE-DECLARATION-GROUP>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroup)
        self.assertEqual(len(elem.mode_transitions), 1)
        mode_transition = elem.mode_transitions[0]
        self.assertEqual(str(mode_transition.entered_mode_ref), entered_mode_ref)
        self.assertEqual(str(mode_transition.exited_mode_ref), exited_mode_ref)

    def test_on_transition_value(self):
        element = ar_element.ModeDeclarationGroup("DeclarationGroupName",
                                                  on_transition_value=4)
        writer = autosar.xml.Writer()
        xml = '''<MODE-DECLARATION-GROUP>
  <SHORT-NAME>DeclarationGroupName</SHORT-NAME>
  <ON-TRANSITION-VALUE>4</ON-TRANSITION-VALUE>
</MODE-DECLARATION-GROUP>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroup = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroup)
        self.assertEqual(elem.on_transition_value, 4)


class TestModeDeclarationGroupPrototype(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ModeDeclarationGroupPrototype("ModeGroup")
        writer = autosar.xml.Writer()
        xml = '''<MODE-DECLARATION-GROUP-PROTOTYPE>
  <SHORT-NAME>ModeGroup</SHORT-NAME>
</MODE-DECLARATION-GROUP-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element, "MODE-DECLARATION-GROUP-PROTOTYPE"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroupPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroupPrototype)
        self.assertEqual(elem.name, "ModeGroup")

    def test_calibration_access(self):
        element = ar_element.ModeDeclarationGroupPrototype("ModeGroup",
                                                           calibration_access=ar_enum.SwCalibrationAccess.READ_ONLY)
        writer = autosar.xml.Writer()
        xml = '''<MODE-DECLARATION-GROUP-PROTOTYPE>
  <SHORT-NAME>ModeGroup</SHORT-NAME>
  <SW-CALIBRATION-ACCESS>READ-ONLY</SW-CALIBRATION-ACCESS>
</MODE-DECLARATION-GROUP-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element, "MODE-DECLARATION-GROUP-PROTOTYPE"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroupPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroupPrototype)
        self.assertEqual(elem.calibration_access, ar_enum.SwCalibrationAccess.READ_ONLY)

    def test_type_ref(self):
        mode_group_ref = "/ModeDeclarations/ModeGroupName/Mode1"
        element = ar_element.ModeDeclarationGroupPrototype("ModeGroup",
                                                           type_ref=mode_group_ref)
        writer = autosar.xml.Writer()
        xml = f'''<MODE-DECLARATION-GROUP-PROTOTYPE>
  <SHORT-NAME>ModeGroup</SHORT-NAME>
  <TYPE-TREF DEST="MODE-DECLARATION-GROUP">{mode_group_ref}</TYPE-TREF>
</MODE-DECLARATION-GROUP-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element, "MODE-DECLARATION-GROUP-PROTOTYPE"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeDeclarationGroupPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeDeclarationGroupPrototype)
        self.assertEqual(str(elem.type_ref), mode_group_ref)


if __name__ == '__main__':
    unittest.main()
