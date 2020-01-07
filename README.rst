AUTOSAR
-------

A set of Python modules for working with `AUTOSAR <https://www.autosar.org/>`_ XML files.

* Allows individuals and teams to incrementally develop and maintain AUTOSAR models using Python code.
* Executing a Python script can quickly regenerate the same ARXML file(s) (no real need to store generated ARXML files in version control).

It is recommended that you use a commercial AUTOSAR toolchain to integrate generated SWCs into your ECU.

Prerequisites
-------------

* `Python 3.x <https://www.python.org/>`_
* `cfile <https://github.com/cogu/cfile/>`_

Documentation
-------------

Documentation is published `here <https://autosar.readthedocs.io/en/latest/>`_.

Current Roadmap
---------------

v0.3.9
~~~~~~

* Fixes
* Improved (AUTOSAR4) documentation
* More comprehensive suite of unit tests


v0.4.0
~~~~~~

* Maintenance track (stable version of v0.3.x)
* v0.4.x will be the last release to support RTE generator for AUTOSAR3

v0.5.0
~~~~~~

* Complete rewrite of RTE generator (upgrade to AUTOSAR4)
* At the same time upgrade the `autosar-demo project <https://github.com/cogu/autosar-demo>`_ to AUTOSAR4
