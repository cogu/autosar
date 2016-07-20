Autosar
--------

A set of python modules for working with AUTOSAR XML files

**Usage:**::

    >>> import autosar
    >>> ws = autosar.workspace()
    >>> ws.append(autosar.Package('DataType'))
    >>> printf(ws.toXML())