#!/usr/bin/env python3
dev_mode = False
if dev_mode:
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import autosar

def create_packages(ws):
    ws.createPackage('DataTypes', role='DataType')
    ws.createPackage('Constants', role="Constant")
    ws.createPackage('PortInterfaces', role="PortInterface")
    ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
    ws.createPackage('ComponentTypes', role='ComponentType')

if __name__ == '__main__':
    ws = autosar.workspace("4.2.2")
    create_packages(ws)
    autosar.util.createDcf(ws).save(dest_dir = 'autosar4', dcf_name = 'Packages',
                                    file_map = {
                                        'DataTypes': {'root': 'DATATYPE', 'filters': ['/DataTypes']},
                                        'Constants': {'root': 'CONSTANT', 'filters': ['/Constants']},
                                        'PortInterfaces': {'root': 'PORTINTERFACE', 'filters': ['/PortInterfaces', '/ModeDclrGroups']},
                                        'ComponentTypes': {'root': 'COMPONENTTYPE', 'filters': ['/ComponentTypes']},
                                        }, force=True)
    print("Done")
