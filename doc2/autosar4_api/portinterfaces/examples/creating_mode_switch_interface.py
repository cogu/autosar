import autosar

ws = autosar.workspace("4.2.2")
modePkg = ws.createPackage('ModeDclrGroups', role = 'ModeDclrGroup')
portInterfacePkg = ws.createPackage('PortInterfaces', role="PortInterface")

modePkg.createModeDeclarationGroup('BswM_Mode', ["POSTRUN",
                                                 "RUN",
                                                 "SHUTDOWN",
                                                 "STARTUP",
                                                 "WAKEUP"], "STARTUP")
portInterfacePkg.createModeSwitchInterface('BSWM_Mode_I', autosar.mode.ModeGroup('mode', '/ModeDclrGroups/BswM_Mode'))
ws.saveXML('PortInterfaces.arxml', filters=['/PortInterfaces'])