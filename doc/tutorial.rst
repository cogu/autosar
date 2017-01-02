Tutorial
========

Datatypes
---------

In this tutorial we will be creating some simple integer data types.

AUTOSAR supports two different kinds of integer data types:
 * Physical datatypes.
 * Enumeration datatypes.

Physical data types have properties like unit, offset and scaling while enumeration types have values and value tables.

Our physical data types for this tutorial:
   
   +----------------+-----+-------+------------+--------+---------+
   | Name           | Min | Max   | Unit       | Offset | Scaling |
   +================+=====+=======+============+========+=========+
   | EngineSpeed_T  | 0   | 65535 | RPM        |   0    |  1/64   |
   +----------------+-----+-------+------------+--------+---------+
   | VehicleSpeed_T | 0   | 65535 | Km/h (Kph) |   0    |   1/8   |
   +----------------+-----+-------+------------+--------+---------+
   | Percent_T      | 0   | 255   | Percent    |   0    |   0.4   |
   +----------------+-----+-------+------------+--------+---------+
   | CoolantTemp_T  | 0   | 255   | Degrees C  |   -40  |   1/2   |
   +----------------+-----+-------+------------+--------+---------+

|

Our enumeration data types (InactiveActive_T, OnOff_T):

    +----------------+-----------------------------+--------------------+
    |  Raw Value     |   InactiveActive_T          |       OnOff_T      |
    +================+=============================+====================+
    |         0      | InactiveActive_Inactive     | OnOff_Off          |
    +----------------+-----------------------------+--------------------+
    |         1      | InactiveActive_Active       | OnOff_On           |
    +----------------+-----------------------------+--------------------+
    |         2      | InactiveActive_Error        | OnOff_Error        |
    +----------------+-----------------------------+--------------------+
    |         3      | InactiveActive_NotAvailable | OnOff_NotAvailable |
    +----------------+-----------------------------+--------------------+
    

First we begin by importing the autosar module. If you have not installed the module yet you should do so now (see :doc:`../start`).

.. code-block:: python

   import autosar
   
   ws=autosar.workspace()

In our newly created workspace we create an AUTOSAR package called 'DataType'. In addition we also create two subpackages called 'DataTypeSemantics' and 'DataTypeUnits'.

The first subpackage we assign a role called 'CompuMethod'. The package with this role will contain information about offset and scaling as well as the value tables for enumration types.

The second subpackage we assign a role called 'Unit'. This package will contain the text strings for our unit names for our physical data types.

.. code-block:: python
   
   dataTypes=ws.createPackage('DataType')
   dataTypes.createSubPackage('DataTypeSemantics', role='CompuMethod')
   dataTypes.createSubPackage('DataTypeUnits', role='Unit')

Next we use the Package.createIntegerDataType method to create our integer types.
This method will do the heavy lifting of creating the necessary objects in our package (DataType) and subpackages (DataTypeSemantics, DataTypeUnits).
It is strongly recommended that you always use the package.createXX set of methods to create all elements in your packages.

.. code-block:: python

   dataTypes.createIntegerDataType('EngineSpeed_T', min=0, max=65535, offset=0, scaling=1/8, unit='rpm')
   dataTypes.createIntegerDataType('VehicleSpeed_T', min=0, max=65535, offset=0, scaling=1/64, unit='kph')
   dataTypes.createIntegerDataType('Percent_T',min=0, max=255, offset=0, scaling=0.4, unit='Percent')
   dataTypes.createIntegerDataType('CoolantTemp_T', min=0, max=255,offset=-40, scaling=0.5, unit='DegreeC')
   print(ws.toXML())

At the end I added a line which prints our work so far to the console. You should get an output like this:

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <AUTOSAR xsi:schemaLocation="http://autosar.org/3.0.2 autosar_302_ext.xsd" xmlns="http://autosar.org/3.0.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <TOP-LEVEL-PACKAGES>
         <AR-PACKAGE>
            <SHORT-NAME>DataType</SHORT-NAME>
            <ELEMENTS>
               <INTEGER-TYPE>
                  <SHORT-NAME>EngineSpeed_T</SHORT-NAME>
                  <SW-DATA-DEF-PROPS>
                     <COMPU-METHOD-REF DEST="COMPU-METHOD">/DataType/DataTypeSemantics/EngineSpeed_T</COMPU-METHOD-REF>
                  </SW-DATA-DEF-PROPS>
                  <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                  <UPPER-LIMIT INTERVAL-TYPE="CLOSED">65535</UPPER-LIMIT>
               </INTEGER-TYPE>
               <INTEGER-TYPE>
                  <SHORT-NAME>VehicleSpeed_T</SHORT-NAME>
                  <SW-DATA-DEF-PROPS>
                     <COMPU-METHOD-REF DEST="COMPU-METHOD">/DataType/DataTypeSemantics/VehicleSpeed_T</COMPU-METHOD-REF>
                  </SW-DATA-DEF-PROPS>
                  <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                  <UPPER-LIMIT INTERVAL-TYPE="CLOSED">65535</UPPER-LIMIT>
               </INTEGER-TYPE>
               <INTEGER-TYPE>
                  <SHORT-NAME>Percent_T</SHORT-NAME>
                  <SW-DATA-DEF-PROPS>
                     <COMPU-METHOD-REF DEST="COMPU-METHOD">/DataType/DataTypeSemantics/Percent_T</COMPU-METHOD-REF>
                  </SW-DATA-DEF-PROPS>
                  <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                  <UPPER-LIMIT INTERVAL-TYPE="CLOSED">255</UPPER-LIMIT>
               </INTEGER-TYPE>
               <INTEGER-TYPE>
                  <SHORT-NAME>CoolantTemp_T</SHORT-NAME>
                  <SW-DATA-DEF-PROPS>
                     <COMPU-METHOD-REF DEST="COMPU-METHOD">/DataType/DataTypeSemantics/CoolantTemp_T</COMPU-METHOD-REF>
                  </SW-DATA-DEF-PROPS>
                  <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
                  <UPPER-LIMIT INTERVAL-TYPE="CLOSED">255</UPPER-LIMIT>
               </INTEGER-TYPE>
            </ELEMENTS>
            <SUB-PACKAGES>
               <AR-PACKAGE>
                  <SHORT-NAME>DataTypeSemantics</SHORT-NAME>
                  <ELEMENTS>
                     <COMPU-METHOD>
                        <SHORT-NAME>EngineSpeed_T</SHORT-NAME>
                        <UNIT-REF DEST="UNIT">/DataType/DataTypeUnits/rpm</UNIT-REF>
                        <COMPU-INTERNAL-TO-PHYS>
                           <COMPU-SCALES>
                              <COMPU-SCALE>
                                 <COMPU-RATIONAL-COEFFS>
                                    <COMPU-NUMERATOR>
                                       <V>0</V>
                                       <V>1</V>
                                    </COMPU-NUMERATOR>
                                    <COMPU-DENOMINATOR>
                                       <V>8</V>
                                    </COMPU-DENOMINATOR>
                                 </COMPU-RATIONAL-COEFFS>
                              </COMPU-SCALE>
                           </COMPU-SCALES>
                        </COMPU-INTERNAL-TO-PHYS>
                     </COMPU-METHOD>
                     <COMPU-METHOD>
                        <SHORT-NAME>VehicleSpeed_T</SHORT-NAME>
                        <UNIT-REF DEST="UNIT">/DataType/DataTypeUnits/kph</UNIT-REF>
                        <COMPU-INTERNAL-TO-PHYS>
                           <COMPU-SCALES>
                              <COMPU-SCALE>
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
                     <COMPU-METHOD>
                        <SHORT-NAME>Percent_T</SHORT-NAME>
                        <UNIT-REF DEST="UNIT">/DataType/DataTypeUnits/Percent</UNIT-REF>
                        <COMPU-INTERNAL-TO-PHYS>
                           <COMPU-SCALES>
                              <COMPU-SCALE>
                                 <COMPU-RATIONAL-COEFFS>
                                    <COMPU-NUMERATOR>
                                       <V>0</V>
                                       <V>0.4</V>
                                    </COMPU-NUMERATOR>
                                    <COMPU-DENOMINATOR>
                                       <V>1</V>
                                    </COMPU-DENOMINATOR>
                                 </COMPU-RATIONAL-COEFFS>
                              </COMPU-SCALE>
                           </COMPU-SCALES>
                        </COMPU-INTERNAL-TO-PHYS>
                     </COMPU-METHOD>
                     <COMPU-METHOD>
                        <SHORT-NAME>CoolantTemp_T</SHORT-NAME>
                        <UNIT-REF DEST="UNIT">/DataType/DataTypeUnits/DegreeC</UNIT-REF>
                        <COMPU-INTERNAL-TO-PHYS>
                           <COMPU-SCALES>
                              <COMPU-SCALE>
                                 <COMPU-RATIONAL-COEFFS>
                                    <COMPU-NUMERATOR>
                                       <V>-40</V>
                                       <V>1</V>
                                    </COMPU-NUMERATOR>
                                    <COMPU-DENOMINATOR>
                                       <V>2</V>
                                    </COMPU-DENOMINATOR>
                                 </COMPU-RATIONAL-COEFFS>
                              </COMPU-SCALE>
                           </COMPU-SCALES>
                        </COMPU-INTERNAL-TO-PHYS>
                     </COMPU-METHOD>
                  </ELEMENTS>
               </AR-PACKAGE>
               <AR-PACKAGE>
                  <SHORT-NAME>DataTypeUnits</SHORT-NAME>
                  <ELEMENTS>
                     <UNIT>
                        <SHORT-NAME>rpm</SHORT-NAME>
                        <DISPLAY-NAME>rpm</DISPLAY-NAME>
                     </UNIT>
                     <UNIT>
                        <SHORT-NAME>kph</SHORT-NAME>
                        <DISPLAY-NAME>kph</DISPLAY-NAME>
                     </UNIT>
                     <UNIT>
                        <SHORT-NAME>Percent</SHORT-NAME>
                        <DISPLAY-NAME>Percent</DISPLAY-NAME>
                     </UNIT>
                     <UNIT>
                        <SHORT-NAME>DegreeC</SHORT-NAME>
                        <DISPLAY-NAME>DegreeC</DISPLAY-NAME>
                     </UNIT>
                  </ELEMENTS>
               </AR-PACKAGE>
            </SUB-PACKAGES>
         </AR-PACKAGE>
      </TOP-LEVEL-PACKAGES>
   </AUTOSAR>

Finally, we add the lines that creates our enumeration types (InactiveActive_T, OnOff_T). We also replace our print to a file save to a new file called 'DataTypes.arxml'

.. code-block:: python

   dataTypes.createIntegerDataType('InactiveActive_T',valueTable=[
        'InactiveActive_Inactive',
        'InactiveActive_Active',
        'InactiveActive_Error',
        'InactiveActive_NotAvailable'])
   
   dataTypes.createIntegerDataType('OnOff_T',valueTable=[
       "OnOff_Off",
       "OnOff_On",
       "OnOff_Error",
       "OnOff_NotAvailable"])
   
    
   ws.saveXML('DataTypes.arxml')

Below you will find the entire script we have written so far.

.. code-block:: python

   import autosar
   
   ws=autosar.workspace()
   
   dataTypes=ws.createPackage('DataType')
   dataTypes.createSubPackage('DataTypeSemantics', role='CompuMethod')
   dataTypes.createSubPackage('DataTypeUnits', role='Unit')
   
   dataTypes.createIntegerDataType('EngineSpeed_T', min=0, max=65535, offset=0, scaling=1/8, unit='rpm')
   dataTypes.createIntegerDataType('VehicleSpeed_T', min=0, max=65535, offset=0, scaling=1/64,unit='kph')
   dataTypes.createIntegerDataType('Percent_T', min=0, max=255, offset=0, scaling=0.4, unit='Percent')
   dataTypes.createIntegerDataType('CoolantTemp_T', min=0, max=255, offset=-40, scaling=0.5, unit='DegreeC')
   dataTypes.createIntegerDataType('InactiveActive_T', valueTable=[
        'InactiveActive_Inactive',
        'InactiveActive_Active',
        'InactiveActive_Error',
        'InactiveActive_NotAvailable'])
   dataTypes.createIntegerDataType('OnOff_T', valueTable=[
       "OnOff_Off",
       "OnOff_On",
       "OnOff_Error",
       "OnOff_NotAvailable"])
   
   ws.saveXML('DataTypes.arxml')

If you run this script you will see a new file being created, called 'DataTypes.arxml'.

Next, create a new python script (in the same directory) and enter the following code:

.. code-block:: python
   
   import autosar
   
   ws = autosar.workspace()
   ws.loadXML('DataTypes.arxml')
   
   for elem in ws['DataType'].elements:
      print("%s: %s"%(elem.name,type(elem)))

This script simply loops over all the elements in the DataType package and print its name and type (ws['DataType'].elements is the list containing all elements of the package 'DataType')

Output:

.. code-block:: bash
   
   EngineSpeed_T: <class 'autosar.datatype.IntegerDataType'>
   VehicleSpeed_T: <class 'autosar.datatype.IntegerDataType'>
   Percent_T: <class 'autosar.datatype.IntegerDataType'>
   CoolantTemp_T: <class 'autosar.datatype.IntegerDataType'>
   InactiveActive_T: <class 'autosar.datatype.IntegerDataType'>
   OnOff_T: <class 'autosar.datatype.IntegerDataType'>
