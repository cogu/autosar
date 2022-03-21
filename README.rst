AUTOSAR
-------

A set of Python modules for working with `AUTOSAR <https://www.autosar.org/>`_ XML files.

* Allows individuals and teams to incrementally develop and maintain AUTOSAR SWC models using Python code.
* Executing a Python script can quickly regenerate the same ARXML file(s) (no real need to store generated ARXML files in version control).

It is recommended that you use a commercial AUTOSAR toolchain to integrate generated SWCs into your ECU.

AUTOSAR version support
-----------------------

* AUTOSAR 3.0
* AUTOSAR 4.2

The intent is to add support for AUTOSAR 4.3 and 4.4 in the future. (Timeplan is unknown since I do most of the work in my spare time.)

Requirements
------------

* `Python 3 <https://www.python.org/>`_
* `cfile <https://github.com/cogu/cfile/>`_

Documentation
-------------

* `Documentation Root <https://autosar.readthedocs.io/en/latest/>`_
* `Installation Guide <https://autosar.readthedocs.io/en/latest/start.html>`_
* `AUTOSAR 4 API <https://autosar.readthedocs.io/en/latest/autosar4_api/>`_

Release Tracks
--------------

Stable (v0.4)
~~~~~~~~~~~~~

This is the stable release track. Only bug fixes and stability improvements will be made.

Latest stable release is `v0.4.0 <https://github.com/cogu/autosar/releases/tag/v0.4.0>`_.

Future work will be tracked on branch *release/0.4*.

Experimental (v0.5)
~~~~~~~~~~~~~~~~~~~

This is the development track for new features. Future changes might break existing APIs from v0.4.x. Use at your own risk.

First release *v0.5.0* is not yet made.

Future work will be tracked on branch *master*.