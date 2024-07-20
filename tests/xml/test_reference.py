"""Unit tests for programmatically building components and save them as XML"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.element as ar_element # noqa E402
import autosar.xml.enumeration as ar_enum  # noqa E402


class TestPortReferences(unittest.TestCase):

    def test_abstract_require_port_prototype_ref(self):

        rport_ref = ar_element.PortPrototypeRef("/ComponentTypes/MyApplicationComponent/RequirePort1",
                                                ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        pport_ref = ar_element.PortPrototypeRef("/ComponentTypes/MyApplicationComponent/ProvidePort1",
                                                ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        ar_element.AbstractRequiredPortPrototypeRef(rport_ref.value, rport_ref.dest)
        with self.assertRaises(ValueError):
            ar_element.AbstractRequiredPortPrototypeRef(pport_ref.value, pport_ref.dest)


if __name__ == '__main__':
    unittest.main()
