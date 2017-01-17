.. AUTOSAR documentation master file, created by
   sphinx-quickstart on Wed Jul 13 19:43:50 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The `AUTOSAR <https://www.autosar.org/>`_ Python Package
========================================================

.. toctree::
   :maxdepth: 2
   :hidden:
      
   start    <start>
   tutorial <tutorial>
   behavior <behavior>
   component <component>
   constant <constant>
   datatype <datatype>   
   package <package>   
   portinterface <portinterface>
   rte <rte>
   workspace <workspace>   
   
What is it?
-----------

This package is a set a set of Python modules for working with `AUTOSAR <https://www.autosar.org/>`_ XML files.

What can it do?
---------------

It can be used for many things, such as:

- Load `AUTOSAR <https://www.autosar.org/>`_ XML files into a python data structure.
- Manipulate, delete or add objects in the data structure.
- Save the data structure back to XML
- Save the data structure as python code that when executed builds up the data structure again.

The primary focus of this project will be on the following `AUTOSAR <https://www.autosar.org/>`_ elements:
 - Workspace
 - Packages
 - Component types
 - Port interfaces
 - Data types
 - Constants
 - ECU Extracts (parsing only)

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

First Read the :doc:`start` guide. After that you should read some of the :doc:`tutorial`.

Current Limitations
-------------------
Currently only supports `AUTOSAR <https://www.autosar.org/>`_ 3.x. Support for `AUTOSAR <https://www.autosar.org/>`_ 4.x will be implemented later.

