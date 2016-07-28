AUTOSAR
--------

A set of python modules for working with `AUTOSAR <https://www.autosar.org/>`_ XML files

**Note: This project is in early stages of development and is probably not very usable as of yet.**

**Usage:**::

    >>> import autosar
    >>> ws = autosar.workspace()
    >>> ws.append(autosar.Package('DataType'))
    >>> print(ws.toXML())

Prerequisites
-------------
Python 3.x (python 2.x will not be supported)

Installation
------------
Download (or clone) the git repo then install using::

>>> python3 setup.py install

Documentation
-------------
The documentation can be found `here <http://autosar.readthedocs.io/en/latest/>`_.