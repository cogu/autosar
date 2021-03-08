import autosar

ws = autosar.workspace(version="4.2.2")
package = ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
package.createModeDeclarationGroup('BswM_Mode', [
                                                "STARTUP",
                                                "RUN",
                                                "POSTRUN",
                                                "WAKEUP",
                                                "SHUTDOWN"
                                                ], "STARTUP")

package.createModeDeclarationGroup('BswM_ModeWithValue', [
                                                (0, "STARTUP"),
                                                (1, "RUN"),
                                                (2, "POSTRUN"),
                                                (3, "WAKEUP"),
                                                (4, "SHUTDOWN")
                                                ], "STARTUP")
print(ws.toXML())
