AUTOSAR
-------

A set of Python modules for working with `AUTOSAR <https://www.autosar.org/>`_ XML files.

The primary purpose of this package is to allow developers to programmatically create AUTOSAR components using Python scripting.

Advantages:

* Python scripts are easy to modify and can be versioned controlled.
* Executing a Python script can quickly regenerate ARXML files (no need to store generated ARXML files under version control).
* Allows teams to incrementally develop and maintain AUTOSAR models using Python.

It is recommended that you use a commercial AUTOSAR toolchain to open and/or integrate ARXML files generated from Python.

Prerequisites
-------------

* `Python 3.x <https://www.python.org/>`_
* `cfile <https://github.com/cogu/cfile/>`_

Documentation
-------------

The Python API and its documentation are currently being reworked in the feature/ar4_api branch. You can find an early preview `here <http://autosar.readthedocs.io/en/latest/>`_.

Upcoming Releases
-----------------

autosar 0.3.6
~~~~~~~~~~~~~~

* New data type API (AUTOSAR4)
* Documentation overhaul (AUTOSAR4)
* Comprehensive unit tests (AUTOSAR3, AUTOSAR4)