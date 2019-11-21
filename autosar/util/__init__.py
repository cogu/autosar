import autosar.util.dcf

def importDcf(filename, external = True):
    """
    Convenience method for importing a DCF file into a newly created workspace
    """
    parser = autosar.util.dcf.DcfParser()
    dcf = parser.parse(filename)
    ws = autosar.workspace()
    dcf.loadReferences(ws, external)
    return ws

def createDcf(ws):
    """
    Convenience method for creating a new Dcf instance based on existing workspace
    """
    return autosar.util.dcf.Dcf(ws)
