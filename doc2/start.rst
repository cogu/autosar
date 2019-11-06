Getting Started
===============

Installation
------------

After you have downloaded and unzipped the module, install it as you would install any other python-module::

   Linux (shell):
   $python3 setup.py install

   Windows (cmd):
   >python setup.py install

Supported AUTOSAR Versions
--------------------------

These are the AUTOSAR versions that this module is known to work with:

* AUTOSAR 3.0.1
* AUTOSAR 4.2.2

Other versions might work for you but they have not been tested by the author of this module.

The workspace object
--------------------

The workspace object is the root object that you use to create, load or save autosar XML files in Python.
You create a new workspace by calling the workspace function:

.. code-block:: python

   import autosar

   ws = autosar.workspace(<version-string>)

Normally you want to create a single workspace object after module import and use that object until the script ends.
In some situations you will create multiple workspaces in the same script. The autosar module has full support for using multiple workspaces.

The version string
~~~~~~~~~~~~~~~~~~

When you create your workspace you should specify which AUTOSAR version you intend to use.
This is important when you intend to export your workspace object as ARXML later on. it's not required when you just want to load an existing XML file.

Example:

.. code-block:: python

   import autosar

   ws = autosar.workspace("4.2.2")


The basics of AUTOSAR XML (ARXML)
---------------------------------

An AUTOSAR XML file is just a normal XML file with the file extension ".arxml". The root XML element is called <AUTOSAR>.
Inside the AUTOSAR (XML) element you will typically a collection of AUTOSAR packages.

Below is an example of a simplifed AUTOSAR XML with 4 empty packages. The packages in this file are simply named "Package1", "Package2, "Package3" and "Package4".

.. code-block:: xml

   <AUTOSAR>
      <AR-PACKAGES>
         <PACKAGE>
            <SHORT-NAME>Package1</SHORT-NAME>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>Package2</SHORT-NAME>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>Package3</SHORT-NAME>
         </PACKAGE>
         <PACKAGE>
            <SHORT-NAME>Package4</SHORT-NAME>
         </PACKAGE>
      </AR-PACKAGES>
   </AUTOSAR>

.. note:: In AUTOSAR v4, the XML-tag where all packages resides is called <AR-PACKAGES>. In AUTOSAR v3 it's called <TOP-LEVEL-PACKAGES>.

You can easily create the above file in Python by following the example below.

.. include:: examples/creating_packages.py
    :code: python


Navigating the XML using references
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any object in the XML that has a name property can be found using a reference string.
A reference is a string describing the objects absolute position within the XML hierarchy.
This is similar in concept to `XPath <https://en.wikipedia.org/wiki/XPath>`_.

The root reference is '/'. This corressponds to the outermost XML node called <AR-PACKAGES>. This is also the root of the workspace object.
Any direct child node that have an inner tag called <SHORT-NAME> can be accessed by adding that name to the root reference.
Deeper nodes can be accessed by adding the '/' character followed by the next child node which in turn contains an inner <SHORT-NAME> tag.
Most Python objects that you will create will have two properties:

* ref (str): Full reference to this object in the ARXML hierarchy.
* name (str): The name of this object. This is the last section of the reference string and will become the <SHORT-NAME> property once exported as ARXML.

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

AUTOSAR Elements
~~~~~~~~~~~~~~~~

Besides a name, every AUTOSAR package contain:

* A list of AUTOSAR Elements (0 or more)
* A list of AUTOSAR Sub-packages (0 or more)

AUTOSAR Elements can be almost anything (except packages). The most commonly used element types are:

* Data Types
* Port Interfaces
* Constants
* Components

In Python, element objects are created by calling methods found in the closest parent object.
Within this documentation these methods are commonly known as *factory methods*.

Package Roles
~~~~~~~~~~~~~

When you are using this Python module to programmatically create AUTOSAR elements it should be as easy to use as possible.
For this purpose we use something called package roles as a hint to Python, telling it which package contain what type of elements.
Package roles are usually set when you create the package but can also be assigned later.

.. table::
   :align: left

   +-------------------+---------------------------+
   | Package Role Name |  Element Types            |
   +===================+===========================+
   | DataType          | Data Types                |
   +-------------------+---------------------------+
   | Constant          | Constants                 |
   +-------------------+---------------------------+
   | ComponentType     | Components (prototypes)   |
   +-------------------+---------------------------+
   | ModeDclrGroup     | Mode Declaration Groups   |
   +-------------------+---------------------------+
   | CompuMethod       | Computational Methods     |
   +-------------------+---------------------------+
   | DataConstraint    | Data Constraints          |
   +-------------------+---------------------------+

.. note:: Package roles are only used within this Python module which means it's not stored anywhere in the XML itself.

Full Example - Creating DataTypes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example we will create two ImplementationDataTypes.


.. table::
   :align: left

   +----------------+----------------+
   | Name           | VehicleSpeed_T |
   +----------------+----------------+
   | Internal Range | 0..65535       |
   +----------------+----------------+
   | Offset         | 0              |
   +----------------+----------------+
   | Scaling:       | 1/64           |
   +----------------+----------------+
   | Unit           | Km/h           |
   +----------------+----------------+

|

.. table::
   :align: left

   +----------------+-----------------------+
   | Name           | OnOff_T               |
   +----------------+-----------------------+
   | Internal Range | 0..3                  |
   +----------------+-----------------------+
   | Enumeration    | * OffOn_Off           |
   |                | * OffOn_On            |
   |                | * OffOn_Error         |
   |                | * OffOn_NotAvailable  |
   +----------------+-----------------------+

In this workspace we choose to create the first datatype as a reference to the native ImplementationDataType uint16.
For the second datatype we choose to create it as a reference to the native ImplementationDataType uint8.

An ImplementationDataType in AUTOSAR is similar in concept to the typedef keyword in the C programming language.

In this example we allow the Python module to automatically create additional elements such as:

* Unit(s)
* Computational Method(s)
* Data Constraint(s)

You can also explicitly create custom versions of these elements and let the new data type reference those instead.
You can also turn off implicit creation of these extra elements (such as data constraints) should you want to.

.. include:: examples/creating_datatypes.py
    :code: python3

Output:

.. code-block:: text

   dt1.name: OffOn_T
   dt1.ref: /DataTypes/OffOn_T
   dt2.name: VehicleSpeed_T
   dt2.ref: /DataTypes/VehicleSpeed_T

DataTypes.arxml:

.. code-block:: xml

   <AUTOSAR>
     <AR-PACKAGES>
       <AR-PACKAGE>
         <SHORT-NAME>DataTypes</SHORT-NAME>
         <ELEMENTS>
           <IMPLEMENTATION-DATA-TYPE>
             <SHORT-NAME>uint8</SHORT-NAME>
             <CATEGORY>VALUE</CATEGORY>
             <SW-DATA-DEF-PROPS>
               <SW-DATA-DEF-PROPS-VARIANTS>
                 <SW-DATA-DEF-PROPS-CONDITIONAL>
                   <BASE-TYPE-REF DEST="SW-BASE-TYPE">/DataTypes/BaseTypes/uint8</BASE-TYPE-REF>
                   <SW-CALIBRATION-ACCESS>NOT-ACCESSIBLE</SW-CALIBRATION-ACCESS>
                   <DATA-CONSTR-REF DEST="DATA-CONSTR">/DataTypes/DataConstrs/uint8_DataConstr</DATA-CONSTR-REF>
                 </SW-DATA-DEF-PROPS-CONDITIONAL>
               </SW-DATA-DEF-PROPS-VARIANTS>
             </SW-DATA-DEF-PROPS>
             <TYPE-EMITTER>Platform_Type</TYPE-EMITTER>
           </IMPLEMENTATION-DATA-TYPE>
           <IMPLEMENTATION-DATA-TYPE>
             <SHORT-NAME>uint16</SHORT-NAME>
             <CATEGORY>VALUE</CATEGORY>
             <SW-DATA-DEF-PROPS>
               <SW-DATA-DEF-PROPS-VARIANTS>
                 <SW-DATA-DEF-PROPS-CONDITIONAL>
                   <BASE-TYPE-REF DEST="SW-BASE-TYPE">/DataTypes/BaseTypes/uint16</BASE-TYPE-REF>
                   <SW-CALIBRATION-ACCESS>NOT-ACCESSIBLE</SW-CALIBRATION-ACCESS>
                   <DATA-CONSTR-REF DEST="DATA-CONSTR">/DataTypes/DataConstrs/uint16_DataConstr</DATA-CONSTR-REF>
                 </SW-DATA-DEF-PROPS-CONDITIONAL>
               </SW-DATA-DEF-PROPS-VARIANTS>
             </SW-DATA-DEF-PROPS>
             <TYPE-EMITTER>Platform_Type</TYPE-EMITTER>
           </IMPLEMENTATION-DATA-TYPE>
           <IMPLEMENTATION-DATA-TYPE>
             <SHORT-NAME>OffOn_T</SHORT-NAME>
             <CATEGORY>TYPE_REFERENCE</CATEGORY>
             <SW-DATA-DEF-PROPS>
               <SW-DATA-DEF-PROPS-VARIANTS>
                 <SW-DATA-DEF-PROPS-CONDITIONAL>
                   <SW-CALIBRATION-ACCESS>NOT-ACCESSIBLE</SW-CALIBRATION-ACCESS>
                   <COMPU-METHOD-REF DEST="COMPU-METHOD">/DataTypes/CompuMethods/OffOn_T</COMPU-METHOD-REF>
                   <DATA-CONSTR-REF DEST="DATA-CONSTR">/DataTypes/DataConstrs/OffOn_T_DataConstr</DATA-CONSTR-REF>
                   <IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/uint8</IMPLEMENTATION-DATA-TYPE-REF>
                 </SW-DATA-DEF-PROPS-CONDITIONAL>
               </SW-DATA-DEF-PROPS-VARIANTS>
             </SW-DATA-DEF-PROPS>
           </IMPLEMENTATION-DATA-TYPE>
           <IMPLEMENTATION-DATA-TYPE>
             <SHORT-NAME>VehicleSpeed_T</SHORT-NAME>
             <CATEGORY>TYPE_REFERENCE</CATEGORY>
             <SW-DATA-DEF-PROPS>
               <SW-DATA-DEF-PROPS-VARIANTS>
                 <SW-DATA-DEF-PROPS-CONDITIONAL>
                   <SW-CALIBRATION-ACCESS>NOT-ACCESSIBLE</SW-CALIBRATION-ACCESS>
                   <COMPU-METHOD-REF DEST="COMPU-METHOD">/DataTypes/CompuMethods/VehicleSpeed_T</COMPU-METHOD-REF>
                   <DATA-CONSTR-REF DEST="DATA-CONSTR">/DataTypes/DataConstrs/VehicleSpeed_T_DataConstr</DATA-CONSTR-REF>
                   <IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/uint16</IMPLEMENTATION-DATA-TYPE-REF>
                   <UNIT-REF DEST="UNIT">/DataTypes/Units/KmPerHour</UNIT-REF>
                 </SW-DATA-DEF-PROPS-CONDITIONAL>
               </SW-DATA-DEF-PROPS-VARIANTS>
             </SW-DATA-DEF-PROPS>
           </IMPLEMENTATION-DATA-TYPE>
         </ELEMENTS>
         <AR-PACKAGES>
           <AR-PACKAGE>
             <SHORT-NAME>CompuMethods</SHORT-NAME>
             <ELEMENTS>
               <COMPU-METHOD>
                 <SHORT-NAME>OffOn_T</SHORT-NAME>
                 <CATEGORY>TEXTTABLE</CATEGORY>
                 <COMPU-INTERNAL-TO-PHYS>
                   <COMPU-SCALES>
                     <COMPU-SCALE>
                       <SHORT-LABEL>OffOn_Off</SHORT-LABEL>
                       <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                       <UPPER-LIMIT INTERVAL-TYPE="CLOSED">0</UPPER-LIMIT>
                       <COMPU-CONST>
                         <VT>OffOn_Off</VT>
                       </COMPU-CONST>
                     </COMPU-SCALE>
                     <COMPU-SCALE>
                       <SHORT-LABEL>OffOn_On</SHORT-LABEL>
                       <LOWER-LIMIT INTERVAL-TYPE="CLOSED">1</LOWER-LIMIT>
                       <UPPER-LIMIT INTERVAL-TYPE="CLOSED">1</UPPER-LIMIT>
                       <COMPU-CONST>
                         <VT>OffOn_On</VT>
                       </COMPU-CONST>
                     </COMPU-SCALE>
                     <COMPU-SCALE>
                       <SHORT-LABEL>OffOn_Error</SHORT-LABEL>
                       <LOWER-LIMIT INTERVAL-TYPE="CLOSED">2</LOWER-LIMIT>
                       <UPPER-LIMIT INTERVAL-TYPE="CLOSED">2</UPPER-LIMIT>
                       <COMPU-CONST>
                         <VT>OffOn_Error</VT>
                       </COMPU-CONST>
                     </COMPU-SCALE>
                     <COMPU-SCALE>
                       <SHORT-LABEL>OffOn_NotAvailable</SHORT-LABEL>
                       <LOWER-LIMIT INTERVAL-TYPE="CLOSED">3</LOWER-LIMIT>
                       <UPPER-LIMIT INTERVAL-TYPE="CLOSED">3</UPPER-LIMIT>
                       <COMPU-CONST>
                         <VT>OffOn_NotAvailable</VT>
                       </COMPU-CONST>
                     </COMPU-SCALE>
                   </COMPU-SCALES>
                 </COMPU-INTERNAL-TO-PHYS>
               </COMPU-METHOD>
               <COMPU-METHOD>
                 <SHORT-NAME>VehicleSpeed_T</SHORT-NAME>
                 <CATEGORY>LINEAR</CATEGORY>
                 <UNIT-REF DEST="UNIT">/DataTypes/Units/KmPerHour</UNIT-REF>
                 <COMPU-INTERNAL-TO-PHYS>
                   <COMPU-SCALES>
                     <COMPU-SCALE>
                       <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                       <UPPER-LIMIT INTERVAL-TYPE="CLOSED">65535</UPPER-LIMIT>
                       <COMPU-RATIONAL-COEFFS>
                         <COMPU-NUMERATOR>
                           <V>0</V>
                           <V>1</V>
                         </COMPU-NUMERATOR>
                         <COMPU-DENOMINATOR>
                           <V>64</V>
                         </COMPU-DENOMINATOR>
                       </COMPU-RATIONAL-COEFFS>
                     </COMPU-SCALE>
                   </COMPU-SCALES>
                 </COMPU-INTERNAL-TO-PHYS>
               </COMPU-METHOD>
             </ELEMENTS>
           </AR-PACKAGE>
           <AR-PACKAGE>
             <SHORT-NAME>DataConstrs</SHORT-NAME>
             <ELEMENTS>
               <DATA-CONSTR>
                 <SHORT-NAME>uint8_DataConstr</SHORT-NAME>
                 <DATA-CONSTR-RULES>
                   <DATA-CONSTR-RULE>
                     <INTERNAL-CONSTRS>
                       <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                       <UPPER-LIMIT INTERVAL-TYPE="CLOSED">255</UPPER-LIMIT>
                     </INTERNAL-CONSTRS>
                   </DATA-CONSTR-RULE>
                 </DATA-CONSTR-RULES>
               </DATA-CONSTR>
               <DATA-CONSTR>
                 <SHORT-NAME>uint16_DataConstr</SHORT-NAME>
                 <DATA-CONSTR-RULES>
                   <DATA-CONSTR-RULE>
                     <INTERNAL-CONSTRS>
                       <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                       <UPPER-LIMIT INTERVAL-TYPE="CLOSED">65535</UPPER-LIMIT>
                     </INTERNAL-CONSTRS>
                   </DATA-CONSTR-RULE>
                 </DATA-CONSTR-RULES>
               </DATA-CONSTR>
               <DATA-CONSTR>
                 <SHORT-NAME>OffOn_T_DataConstr</SHORT-NAME>
                 <DATA-CONSTR-RULES>
                   <DATA-CONSTR-RULE>
                     <INTERNAL-CONSTRS>
                       <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                       <UPPER-LIMIT INTERVAL-TYPE="CLOSED">3</UPPER-LIMIT>
                     </INTERNAL-CONSTRS>
                   </DATA-CONSTR-RULE>
                 </DATA-CONSTR-RULES>
               </DATA-CONSTR>
               <DATA-CONSTR>
                 <SHORT-NAME>VehicleSpeed_T_DataConstr</SHORT-NAME>
                 <DATA-CONSTR-RULES>
                   <DATA-CONSTR-RULE>
                     <INTERNAL-CONSTRS>
                       <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                       <UPPER-LIMIT INTERVAL-TYPE="CLOSED">65535</UPPER-LIMIT>
                     </INTERNAL-CONSTRS>
                   </DATA-CONSTR-RULE>
                 </DATA-CONSTR-RULES>
               </DATA-CONSTR>
             </ELEMENTS>
           </AR-PACKAGE>
           <AR-PACKAGE>
             <SHORT-NAME>Units</SHORT-NAME>
             <ELEMENTS>
               <UNIT>
                 <SHORT-NAME>KmPerHour</SHORT-NAME>
                 <DISPLAY-NAME>KmPerHour</DISPLAY-NAME>
               </UNIT>
             </ELEMENTS>
           </AR-PACKAGE>
           <AR-PACKAGE>
             <SHORT-NAME>BaseTypes</SHORT-NAME>
             <ELEMENTS>
               <SW-BASE-TYPE>
                 <SHORT-NAME>uint8</SHORT-NAME>
                 <CATEGORY>FIXED_LENGTH</CATEGORY>
                 <BASE-TYPE-SIZE>8</BASE-TYPE-SIZE>
                 <BASE-TYPE-ENCODING>NONE</BASE-TYPE-ENCODING>
                 <NATIVE-DECLARATION>uint8</NATIVE-DECLARATION>
               </SW-BASE-TYPE>
               <SW-BASE-TYPE>
                 <SHORT-NAME>uint16</SHORT-NAME>
                 <CATEGORY>FIXED_LENGTH</CATEGORY>
                 <BASE-TYPE-SIZE>16</BASE-TYPE-SIZE>
                 <BASE-TYPE-ENCODING>NONE</BASE-TYPE-ENCODING>
                 <NATIVE-DECLARATION>uint16</NATIVE-DECLARATION>
               </SW-BASE-TYPE>
             </ELEMENTS>
           </AR-PACKAGE>
         </AR-PACKAGES>
       </AR-PACKAGE>
     </AR-PACKAGES>
   </AUTOSAR>
