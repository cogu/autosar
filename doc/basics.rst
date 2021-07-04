.. _basic_concepts:

Basic Concepts
==============

This document describes the basic concepts of AUTOSAR and how you work with them from Python.

.. _basic_arxml:

ARXML
-----

An AUTOSAR XML file or ARXML for short is just a normal XML file with the file extension ".arxml". The root XML element is called <AUTOSAR>.
Inside the AUTOSAR (XML) element you will typically a collection of AUTOSAR packages each containing elements.

.. code-block:: xml

   <AUTOSAR>
      <AR-PACKAGES>
         <PACKAGE>
            <SHORT-NAME>Package1</SHORT-NAME>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>Package2</SHORT-NAME>
         </PACKAGE>
      </AR-PACKAGES>
   </AUTOSAR>

.. _basic_workspace:

Workspace
---------

The AUTOSAR :ref:`workspace <ar4_workspace>` object is the root object that you use to create, load or save AUTOSAR XML files in Python.
You create a new :ref:`workspace <ar4_workspace>` instance by calling the :ref:`autosar.workspace<ar4_autosar_workspace_method>` factory method.

.. code-block:: python

   import autosar

   ws = autosar.workspace()

AUTOSAR Version
~~~~~~~~~~~~~~~

When you create your workspace you should specify which AUTOSAR version you intend to use. By default an AUTOSAR v3.0 workspace is created.

Example:

   .. code-block:: python

      import autosar

      ws = autosar.workspace("4.2.2") #Creates an AUTOSAR v4.2.2 workspace

When loading ARXML from file you do not need to manually set the version. The AUTOSAR version is read from the ARXML file.

.. _basic_packages:

Packages
--------

An AUTOSAR :ref:`ar4_package_Package` is a container for your :ref:`elements <basic_elements>`. It can also contain sub-packages. 
Packages offers a way to separate your elements into different categories such as SWC namespaces or by element types.

Use the :ref:`Workspace.createPackage <ar4_workspace_Workspace_createPackage>` method to create new packages in your :ref:`workspace <ar4_workspace>`.

Use the :ref:`Package.createSubPackage <ar4_package_Package_createSubPackage>` mehod to create a new sub-package inside an existing :ref:`ar4_package_Package`.

.. _basic_elements:

Elements
--------

Elements are what you create and place in your :ref:`packages <ar4_package_Package>`. There are different sub-packages in Python for different 
categories of elements:

* Components
* Constants
* DataTypes
* Modes
* Ports
* PortInterfaces

The :ref:`ar4_package_Package` class offers a wide range of :ref:`ar4_package_Package_methods` to create new elements. These are called *factory methods*.

Element classes derives from the class :ref:`autosar.element.Element <ar4_element_Element>`.

.. _basic_short_name:

Short Name
----------

Every package and element has a *name* attribute (or property). This corresponds to the inner text value of the <SHORT-NAME> tag of the underlying :ref:`basic_arxml`.

References
~~~~~~~~~~

A reference is a string describing the objects absolute position within the XML hierarchy.
This is similar in concept to `XPath <https://en.wikipedia.org/wiki/XPath>`_.

In the XML, the root reference is '/'. This corressponds to the outermost XML node called <AR-PACKAGES>.
This is also the root of the :ref:`workspace <ar4_workspace>`.
Any direct child node that have an inner tag called <SHORT-NAME> can be accessed by adding that name to the root reference.
Deeper nodes can be accessed by adding the '/' character followed by the next child node which in turn contains an inner <SHORT-NAME> tag.
Most Python objects that you will create will have two properties:

* ref (str): Reference string of the object.
* name (str): The name of this object. This corresponds to the inner value of the <SHORT-NAME> XML tag.

Example
~~~~~~~

.. include:: examples/print_elem_refs.py
    :code: python3

Output:

.. code-block:: text

   u8Type.name: uint8
   u8Type.ref: /DataTypes/BaseTypes/uint8
   u16Type.name: uint16
   u16Type.ref: /DataTypes/BaseTypes/uint16
   u32Type.name: uint32
   u32Type.ref: /DataTypes/BaseTypes/uint32

Package Roles
~~~~~~~~~~~~~

When you are using this Python module to programmatically create AUTOSAR elements it should be as easy to use as possible.
For this purpose we use something called package roles as a hint to Python, telling it which package contain what type of elements.
Package roles are usually set when you create the package but can also be assigned later.

For a list of package role names see the :ref:`Package class <ar4_package_Package_roles>`.

For a list of methods related to package roles see the :ref:`Workspace class <ar4_workspace_methods>`.

.. note:: Package roles are only used by the Python package which means it's not stored anywhere in the XML itself.

