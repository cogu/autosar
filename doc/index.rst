.. AUTOSAR documentation master file, created by
   sphinx-quickstart on Wed Jul 13 19:43:50 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The `AUTOSAR <https://www.autosar.org/>`_ Python Package
========================================================

.. toctree::
   :maxdepth: 2
   :hidden:
      
   start
   tutorial/index
   constant/index
   component/index
   

What is it?
-----------

This package is a set a set of Python modules for working with `AUTOSAR <https://www.autosar.org/>`_ XML files.

What can it do?
---------------

It can be used for many things, such as:

- Importing `AUTOSAR <https://www.autosar.org/>`_ XML files into Python.
- Finding objects (packages or elements) from the in-memory data structure.
- Manipulate, delete or add objects in the data structure.
- Export your work back to XML.

The primary focus of this project will be on the following `AUTOSAR <https://www.autosar.org/>`_ elements:
 - Packages
 - ComponentTypes
 - PortInterfaces
 - DataTypes
 - Constants
 - ECU Extracts (parsing only)

Out of scope
------------
Everything else. The `AUTOSAR <https://www.autosar.org/>`_ XML format supports many other constructs such as BSW-configurations and ECU-configurations all which are out of scope for this project.

Prerequisites
-------------
Python 3.x 

Installation
------------
Download (or clone) the git repo from `github <https://github.com/cogu/autosar>`_.

install using::

>>> Python3 setup.py install

Getting Started
---------------

First Read the :doc:`start` guide. After that you should read some of the :doc:`tutorial/index`.

Current Limitations
-------------------
Currently only supports `AUTOSAR <https://www.autosar.org/>`_ 3.x. Support for `AUTOSAR <https://www.autosar.org/>`_ 4.x will be implemented later.

