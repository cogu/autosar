Getting Started
===============

Installation
------------

Installing the cfile package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First install the cfile package.

PIP Install
^^^^^^^^^^^

  $pip3 install cfile


Manual Install
^^^^^^^^^^^^^^

Download latest release from the `cfile Github page <https://github.com/cogu/cfile/releases>`_.

Unzip the release then install using setuptools.

  Linux (shell):
  $python3 setup.py install

  Windows (cmd):
  >python setup.py install

Installing the autosar package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PIP Install
^^^^^^^^^^^

The autosar package is not yet available on `PyPI <https://pypi.org/>`_. 

Manual Install
^^^^^^^^^^^^^^

Download latest release from the `autosar Github page <https://github.com/cogu/autosar/releases>`_.

Unzip the release then install using setuptools.

   Linux (shell):
   $python3 setup.py install

   Windows (PowerShell):
   >python setup.py install

Running Unit Tests
------------------

In case you want to run unit tests you can use the convenience shell scripts to trigger Python to run test cases.

  Linux (shell):
  $./run_tests.sh

  Windows (PowerShell):
  >.\run_tests.cmd

Generating ARXML
----------------

The primary purpose of the Python AUTOSAR package is to programmatically create contents of AUTOSAR XML files or ARXML for short.

Below is a simple example you can use to see if your installation works as expected.

.. include:: examples/creating_data_type_packages.py
    :code: python

Here is what  the script does:

* Creates an AUTOSAR :ref:`ar4_workspace`.
* Creates an AUTOSAR :ref:`ar4_package_Package` hierarchy.
* Creates a :ref:`ar4_datatype_SwBaseType` named *uint8*.
* Creates an :ref:`ar4_datatype_ImplementationDataType` also named *uint8*.
* Saves the workspace under file name *DataTypes.arxml*.

If you are new to the AUTOSAR Python package you should continue by reading more about :ref:`basic_concepts`.