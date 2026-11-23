from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import autosar
import autosar.rte


class TypeGeneratorTest(unittest.TestCase):

    def test_emits_dependencies_before_nested_types(self):
        ws = autosar.workspace(version='3.0.2')
        data_types = ws.createPackage('DataType', role='DataType')
        scalar = data_types.createIntegerDataType('UInt16', min=0, max=65535)
        values = data_types.createArrayDataType('U16Array_T', scalar.ref, 4)
        record = data_types.createRecordDataType('MyRecord_T', [('Values', values.ref)])
        records = data_types.createArrayDataType('ARecordArray_T', record.ref, 2)

        interfaces = ws.createPackage('PortInterface', role='PortInterface')
        interface = interfaces.createSenderReceiverInterface(
            'Output_I', autosar.DataElement('Records', records.ref))
        components = ws.createPackage('ComponentType', role='ComponentType')
        swc = components.createApplicationSoftwareComponent('TestComponent')
        swc.createProvidePort('Output', interface.ref)
        partition = autosar.rte.Partition()
        partition.addComponent(swc)

        with TemporaryDirectory() as dest_dir:
            autosar.rte.TypeGenerator(partition).generate(dest_dir)
            header = (Path(dest_dir) / 'Rte_Type.h').read_text()

        for declaration, use in (
            ('typedef uint16 UInt16;', 'typedef UInt16 U16Array_T[4];'),
            ('typedef UInt16 U16Array_T[4];', 'U16Array_T Values;'),
            ('} MyRecord_T;', 'typedef MyRecord_T ARecordArray_T[2];'),
        ):
            with self.subTest(declaration=declaration, use=use):
                self.assertLess(header.index(declaration), header.index(use))
