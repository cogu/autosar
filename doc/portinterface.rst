:mod:`autosar.portinterface` --- PortInterfaces
===============================================

.. _PortInterface:

   .. py:class:: SenderReceiverPortInterface(name, isService=False, parent=None, adminData=None)

      Represents an AUTOSAR constant specification.
      
      **Usage:**
      
      .. code-block:: python
         
         import autosar
         
         ws = autosar.workspace()
         ws.loadXML('DataTypes.arxml', roles={'/DataType': 'DataType'}) #loads a package named "DataType" from "DataTypes.arxml"
      
         package = ws.createPackage('PortInterface', role='PortInterface')
         package.createSenderReceiverInterface("ABSOffRoadStatus_I", autosar.DataElement('ABSOffRoadStatus', 'OffOn_T'))
         package.createSenderReceiverInterface("ProhibitControlStatus_I", autosar.DataElement('ProhibitControlStatus', 'InactiveActive_T'))   
         ws.saveXML('PortInterfaces.arxml', packages=['PortInterface'])

         
   .. py:attribute:: SenderReceiverPortInterface.name
   
      name of the port interface           
      
   .. py:attribute:: SenderReceiverPortInterface.isService
      
      boolean value for selecting if this interface is a service interface

   .. py:attribute:: SenderReceiverPortInterface.parent
   
      Reference to parent object (usually the package its attached to)
   
   .. py:attribute:: SenderReceiverPortInterface.adminData
   
      Optional admin data
      