import autosar.util.dcf

def importDcf(filename, external = True):
    """
    Convenience for importing a DCF file into a newly created workspace
    """
    parser = autosar.util.dcf.DcfParser()
    dcf = parser.parse(filename)
    ws = autosar.workspace()
    dcf.loadReferences(ws, external)
    return ws
