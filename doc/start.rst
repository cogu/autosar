Getting Started
===============
   
Installation
------------
Module installation:
---------------------
   
After you have downloaded and unzipped the module, install it as you would install any other python-module::
   
   Linux (shell):
   $python3 setup.py install

   Windows (cmd):
   >python setup.py install


The Workspace
-------------

The workspace object is the root object that you use to create, load or save autosar XML files.
You create a new workspace by calling the workspace function in the autosar module:

.. code-block:: python

   import autosar
   
   ws=autosar.workspace()

Normally you will create a workspace object directly after module import and use that object until the script ends.
We will encounter situations later where we will use multiple workspace objects at the same time.

AUTOSAR Packages
----------------

This python module is made for working with AUTOSAR XML files. An AUTOSAR XML file is just a normal XML file with the file extension ".arxml".

In a typical AUTOSAR XML file you will find one or more packages. each package can be seen as a generic container of elements where elements can be almost anything from datatypes to components.
Here's an example of a simplifed AUTOSAR XML with 4 empty packages:

.. code-block:: xml

   <AUTOSAR>
      <TOP-LEVEL-PACKAGES>
         <PACKAGE>
            <SHORT-NAME>Package1</SHORT-NAME>
            <ELEMENTS>
            </ELEMENTS>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>Package2</SHORT-NAME>
            <ELEMENTS>
            </ELEMENTS>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>Package3</SHORT-NAME>
            <ELEMENTS>
            </ELEMENTS>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>Package4</SHORT-NAME>
            <ELEMENTS>
            </ELEMENTS>
         </PACKAGE>
      </TOP-LEVEL-PACKAGES>
   </AUTOSAR>   

The packages in this file are simply named "Package1", "Package2, "Package3" and "Package4". All the elements for each package will go in between the <ELEMENTS> and </ELEMENTS> tags.

As you can see, the package acts as a grouping of elements.
In most cases you would want to group elements of the same kind into one package (e.g. data types) and elements of another kind (e.g. components) into another package.
A very often used package naming convention is as follows.

   * DataType - Contains all data types
   * Constant - Contains all init-values
   * PortInterface - Contains all port interfaces
   * ComponentType - Contains all components

Replacing the generic package names from the XML above with the names from the naming convention list we get the following XML:

.. code-block:: xml

   <AUTOSAR>
      <TOP-LEVEL-PACKAGES>
         <PACKAGE>
            <SHORT-NAME>DataType</SHORT-NAME>
            <ELEMENTS>
            </ELEMENTS>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>Constant</SHORT-NAME>
            <ELEMENTS>
            </ELEMENTS>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>PortInterface</SHORT-NAME>
            <ELEMENTS>
            </ELEMENTS>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>ComponentType</SHORT-NAME>
            <ELEMENTS>
            </ELEMENTS>
         </PACKAGE>
      </TOP-LEVEL-PACKAGES>
   </AUTOSAR>
   
.. comment
   In AUTOSAR v4.x, the XML-tag where all packages resides is called <AR-PACKAGES>. In AUTOSAR v3.x it is called <TOP-LEVEL-PACKAGES>.

