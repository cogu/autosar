Autosar
--------

A set of python modules for working with AUTOSAR XML files

**Note: This project is in early stages of development and is probably not very usable as of yet.**

**Usage:**::

    >>> import autosar
    >>> ws = autosar.workspace()
    >>> ws.append(autosar.Package('DataType'))
    >>> print(ws.toXML())
