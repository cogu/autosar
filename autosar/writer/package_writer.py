from autosar.writer.writer_base import WriterBase
from autosar.writer.datatype_writer import DataTypeWriter
from autosar.writer.constant_writer import ConstantWriter
from autosar.writer.component_writer import ComponentTypeWriter
from autosar.writer.behavior_writer import BehaviorWriter
from autosar.writer.portinterface_writer import PortInterfaceWriter


class PackageWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
      self.dataTypeWriter = DataTypeWriter(version)
      self.constantWriter = ConstantWriter(version)
      self.componentTypeWriter = ComponentTypeWriter(version)
      self.behaviorWriter = BehaviorWriter(version)
      self.portInterfaceWriter = PortInterfaceWriter(version)
      if self.version >= 3.0:
         self.switcherXML = {'ARRAY-TYPE': None,
                          'BOOLEAN-TYPE': None,
                          'IntegerDataType': self.dataTypeWriter.writeIntegerTypeXML,
                          'REAL-TYPE': None,
                          'RecordDataType': self.dataTypeWriter.writeRecordDataTypeXML,
                          'STRING-TYPE': None,
                          'ApplicationSoftwareComponent': self.componentTypeWriter.writeApplicationSoftwareComponentXML,
                          'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE': None,
                          'InternalBehavior': self.behaviorWriter.writeInternalBehaviorXML,
                          'SWC-IMPLEMENTATION': None,
                          'CompuMethodConst': self.dataTypeWriter.writeCompuMethodXML,
                          'CompuMethodRational': self.dataTypeWriter.writeCompuMethodXML,
                          'DataTypeUnitElement': self.dataTypeWriter.writeDataTypeUnitElementXML,
                          'SoftwareAddressMethod': self.portInterfaceWriter.writeSoftwareAddressMethodXML,
                          'ModeDeclarationGroup': self.portInterfaceWriter.writeModeDeclarationGroupXML,
                          'SenderReceiverInterface': self.portInterfaceWriter.writeSenderReceiverInterfaceXML,
                          'ParameterInterface': self.portInterfaceWriter.writeParameterInterfaceXML,
                          'ClientServerInterface': self.portInterfaceWriter.writeClientServerInterfaceXML,
                          'Constant': self.constantWriter.writeConstantXML,
                          'COMPOSITION-TYPE': None,
                          'SYSTEM-SIGNAL': None,
                          'SYSTEM': None
                          }
         self.switcherCode = {'ARRAY-TYPE': None,
                          'BOOLEAN-TYPE': None,
                          'IntegerDataType': None,
                          'REAL-TYPE': None,
                          'RECORD-TYPE': None,
                          'STRING-TYPE': None,
                          'ApplicationSoftwareComponent': self.componentTypeWriter.writeApplicationSoftwareComponentCode,
                          'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE': None,
                          'InternalBehavior': None,
                          'SWC-IMPLEMENTATION': None,
                          'CompuMethodConst': None,
                          'UNIT': None,
                          'SW-ADDR-METHOD': None,
                          'MODE-DECLARATION-GROUP': None,
                          'SenderReceiverInterface': self.portInterfaceWriter.writeSenderReceiverInterfaceCode,
                          'ParameterInterface': self.portInterfaceWriter.writeParameterInterfaceCode,
                          'ClientServerInterface': self.portInterfaceWriter.writeClientServerInterfaceCode,
                          'Constant': None,
                          'COMPOSITION-TYPE': None,
                          'SYSTEM-SIGNAL': None,
                          'SYSTEM': None
                          }
      else:
         raise NotImplementedError("AUTOSAR version not yet supported")
   
   def toXML(self,package):      
      lines=[]
      lines.extend(self.beginPackage(package.name))
      lines.append(self.indent("<ELEMENTS>",1))
      for elem in package.elements:
         writerFunc = self.switcherXML.get(elem.__class__.__name__)
         if writerFunc is not None:            
            lines.extend(self.indent(writerFunc(elem,package),2))
         else:
            print("skipped: %s"%str(type(elem)))
      lines.append(self.indent("</ELEMENTS>",1))
      if len(package.subPackages)>0:
         lines.append(self.indent("<SUB-PACKAGES>",1))
         for subPackage in package.subPackages:
            lines.extend(self.indent(self.toXML(subPackage),2))
         lines.append(self.indent("</SUB-PACKAGES>",1))
      lines.extend(self.endPackage())
      return lines
   
   def toCode(self,package):
      lines=[]
      lines.append('%s=ws.createPackage("%s")'%(package.name,package.name))
      for elem in package.elements:
         writerFunc = self.switcherCode.get(elem.__class__.__name__)
         if writerFunc is not None:
            lines.extend(writerFunc(elem,package))
         else:
            raise NotImplementedError(type(elem))
      return lines
