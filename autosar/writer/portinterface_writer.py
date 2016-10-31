from autosar.writer.writer_base import WriterBase
import autosar.portinterface

class PortInterfaceWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeSenderReceiverInterfaceXML(self, portInterface,package):      
      assert(isinstance(portInterface,autosar.portinterface.SenderReceiverInterface))
      lines=[]      
      lines.append('<SENDER-RECEIVER-INTERFACE>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%portInterface.name,1))
      if portInterface.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(portInterface.adminData),1))
      lines.append(self.indent('<IS-SERVICE>%s</IS-SERVICE>'%self.toBoolean(portInterface.isService),1))
      if len(portInterface.dataElements)>0:
         lines.append(self.indent('<DATA-ELEMENTS>',1))
         for elem in portInterface.dataElements:
            lines.extend(self.indent(self.writeDataElementXML(elem),2))
         lines.append(self.indent('</DATA-ELEMENTS>',1))
      else:
         lines.append(self.indent('<DATA-ELEMENTS/>',1))
      if portInterface.modeGroups is not None:
         lines.append(self.indent('<MODE-GROUPS>',1))
         for group in portInterface.modeGroups:
            lines.extend(self.indent(self.writeModeGroupsXML(group),2))   
         lines.append(self.indent('</MODE-GROUPS>',1))         
      lines.append('</SENDER-RECEIVER-INTERFACE>')      
      return lines

   def writeDataElementXML(self,elem):
      assert(isinstance(elem,autosar.portinterface.DataElement))
      lines=[]
      lines.append('<DATA-ELEMENT-PROTOTYPE>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      ws = elem.rootWS()
      typeElem = ws.find(elem.typeRef)
      if (typeElem is None):
         raise ValueError("invalid type reference: '%s'"%elem.typeRef)
      else:
         lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(typeElem.tag(self.version),typeElem.ref),1))
      lines.append(self.indent('<IS-QUEUED>%s</IS-QUEUED>'%self.toBoolean(elem.isQueued),1))
      lines.append('</DATA-ELEMENT-PROTOTYPE>')
      return lines

   def writeParameterInterfaceXML(self, portInterface,package):
      assert(isinstance(portInterface,autosar.portinterface.ParameterInterface))
      lines=[]
      lines.append('<CALPRM-INTERFACE>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%portInterface.name,1))
      lines.append(self.indent('<IS-SERVICE>%s</IS-SERVICE>'%self.toBoolean(portInterface.isService),1))
      if len(portInterface.dataElements)>0:
         lines.append(self.indent('<CALPRM-ELEMENTS>',1))
         for elem in portInterface.dataElements:
            lines.extend(self.indent(self.writeCalParamElementXML(elem),2))
         lines.append(self.indent('</CALPRM-ELEMENTS>',1))
      else:
         lines.append(self.indent('<CALPRM-ELEMENTS/>',1))
      lines.append('</CALPRM-INTERFACE>')
      return lines
   
   def writeCalParamElementXML(self,elem):
      assert(isinstance(elem,autosar.portinterface.DataElement))
      lines=[]
      lines.append('<CALPRM-ELEMENT-PROTOTYPE>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      ws = elem.rootWS()
      
      if elem.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
      if len(elem.swAddrMethodRefList)>0:
         lines.append(self.indent('<SW-DATA-DEF-PROPS>',1))
         for ref in elem.swAddrMethodRefList:
            swAddrMethodElem=ws.find(ref)
            if (swAddrMethodElem is None):
               raise ValueError("invalid reference: '%s'"%swAddrMethodRef.typeRef)
            else:
               lines.append(self.indent('<SW-ADDR-METHOD-REF DEST="%s">%s</SW-ADDR-METHOD-REF>'%(swAddrMethodElem.tag(self.version),ref),2))
         lines.append(self.indent('</SW-DATA-DEF-PROPS>',1))
      typeElem = ws.find(elem.typeRef)					
      if (typeElem is None):
         raise ValueError("invalid type reference: '%s'"%elem.typeRef)
      else:
         lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(typeElem.tag(self.version),typeElem.ref),1))      
      lines.append('</CALPRM-ELEMENT-PROTOTYPE>')
      return lines
   
   def writeClientServerInterfaceXML(self, portInterface,package):
      assert(isinstance(portInterface,autosar.portinterface.ClientServerInterface))
      lines=[]
      lines.append('<CLIENT-SERVER-INTERFACE>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%portInterface.name,1))
      if portInterface.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(portInterface.adminData),1))
      lines.append(self.indent('<IS-SERVICE>%s</IS-SERVICE>'%self.toBoolean(portInterface.isService),1))
      if len(portInterface.operations)>0:
         lines.append(self.indent('<OPERATIONS>',1))
         for operation in portInterface.operations:
            lines.extend(self.indent(self.writeOperationXML(operation),2))
         lines.append(self.indent('</OPERATIONS>',1))
      else:
         lines.append(self.indent('<OPERATIONS/>',1))
      if len(portInterface.applicationErrors)>0:
         lines.append(self.indent('<POSSIBLE-ERRORS>',1))
         for applicationError in portInterface.applicationErrors:
            lines.extend(self.indent(self.writeApplicationErrorXML(applicationError),2))
         lines.append(self.indent('</POSSIBLE-ERRORS>',1))
      lines.append('</CLIENT-SERVER-INTERFACE>')
      
      return lines
   
   def writeOperationXML(self,operation):
      assert(isinstance(operation,autosar.portinterface.Operation))
      ws = operation.rootWS()
      assert(ws is not None)
      lines=[]
      lines.append('<%s>'%operation.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%operation.name,1))
      if len(operation.arguments)>0:
         lines.append(self.indent('<ARGUMENTS>',1))
         for argument in operation.arguments:
            lines.append(self.indent('<%s>'%argument.tag(),2))
            lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%argument.name,3))
            typeElem = ws.find(argument.typeRef)					
            if (typeElem is None):
               raise ValueError("invalid type reference: '%s'"%argument.typeRef)
            else:
               lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(typeElem.tag(self.version),typeElem.ref),3))      
            lines.append(self.indent('<DIRECTION>%s</DIRECTION>'%argument.direction,3))
            lines.append(self.indent('</%s>'%argument.tag(),2))
         lines.append(self.indent('</ARGUMENTS>',1))
      if len(operation.errorRefs)>0:
         lines.append(self.indent('<POSSIBLE-ERROR-REFS>',1))
         for errorRef in operation.errorRefs:
            errorElem = ws.find(errorRef)
            if (errorElem is None):
               raise ValueError("invalid error reference: '%s'"%errorRef)
            else:
               lines.append(self.indent('<POSSIBLE-ERROR-REF DEST="%s">%s</POSSIBLE-ERROR-REF>'%(errorElem.tag(self.version),errorElem.ref),2))
         lines.append(self.indent('</POSSIBLE-ERROR-REFS>',1))         
      lines.append('</%s>'%operation.tag())
      return lines
   
   def writeApplicationErrorXML(self,applicationError):
      assert(isinstance(applicationError,autosar.portinterface.ApplicationError))
      lines=[]
      lines.append('<%s>'%applicationError.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%applicationError.name,1))
      lines.append(self.indent('<ERROR-CODE>%d</ERROR-CODE>'%applicationError.errorCode,1))
      lines.append('</%s>'%applicationError.tag(self.version))
      return lines
   
   def writeModeGroupsXML(self,modeGroup):
      assert(isinstance(modeGroup,autosar.portinterface.ModeGroup))
      lines=[]
      ws = modeGroup.rootWS()
      assert(ws is not None)
      lines.append('<%s>'%modeGroup.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%modeGroup.name,1))
      typeElem = ws.find(modeGroup.typeRef)					
      if (typeElem is None):
         raise ValueError("invalid type reference: '%s'"%modeGroup.typeRef)
      else:
         lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(typeElem.tag(self.version),typeElem.ref),1))      
      lines.append('</%s>'%modeGroup.tag(self.version))
      return lines
   
   def writeSoftwareAddressMethodXML(self, addressMethod,package):
      assert(isinstance(addressMethod,autosar.portinterface.SoftwareAddressMethod))
      lines=[]
      lines.append('<%s>'%addressMethod.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%addressMethod.name,1))      
      lines.append('</%s>'%addressMethod.tag(self.version))
      return lines
   
   def writeModeDeclarationGroupXML(self, modeDeclGroup,package):
      assert(isinstance(modeDeclGroup,autosar.portinterface.ModeDeclarationGroup))
      lines=[]
      ws = modeDeclGroup.rootWS()
      assert(ws is not None)

      lines.append('<%s>'%modeDeclGroup.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%modeDeclGroup.name,1))
      if modeDeclGroup.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(modeDeclGroup.adminData),1))
      if modeDeclGroup.initialModeRef is not None:
         modeElem = ws.find(modeDeclGroup.initialModeRef)					
         if (modeElem is None):
            raise ValueError("invalid mode reference: '%s'"%modeDeclGroup.typeRef)
         else:
            lines.append(self.indent('<INITIAL-MODE-REF DEST="%s">%s</INITIAL-MODE-REF>'%(modeElem.tag(self.version),modeElem.ref),1))
      if len(modeDeclGroup.modeDeclarations)>0:
         lines.append(self.indent('<MODE-DECLARATIONS>',1))
         for elem in modeDeclGroup.modeDeclarations:         
            lines.append(self.indent('<%s>'%elem.tag(self.version),2))
            lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,3))
            lines.append(self.indent('</%s>'%elem.tag(self.version),2))
         lines.append(self.indent('</MODE-DECLARATIONS>',1))
      lines.append('</%s>'%modeDeclGroup.tag(self.version))
      return lines


					# 
					# <MODE-DECLARATIONS>
					# 	<MODE-DECLARATION>
					# 		<SHORT-NAME>FULL_COMMUNICATION</SHORT-NAME>
					# 	</MODE-DECLARATION>
					# 	<MODE-DECLARATION>
					# 		<SHORT-NAME>NO_COMMUNICATION</SHORT-NAME>
					# 	</MODE-DECLARATION>
					# 	<MODE-DECLARATION>
					# 		<SHORT-NAME>SILENT_COMMUNICATION</SHORT-NAME>
					# 	</MODE-DECLARATION>
					# </MODE-DECLARATIONS>

#### CODE GENERATOTS ####

   def writeSenderReceiverInterfaceCode(self, portInterface,package):
      assert(isinstance(portInterface,autosar.portinterface.SenderReceiverInterface))
      lines=[]
      if len(portInterface.dataElements)==1:
         dataElementCode=self.writeDataElementCode(portInterface.dataElements[0])
         lines.append('%s.createSenderReceiverInterface("%s",%s)'%(package.name,portInterface.name,dataElementCode))
      elif len(portInterface.dataElements)>1:
         raise NotImplementedError('more than one data element in an interface not yet supported')      
      return lines
   
   def writeDataElementCode(self,elem):            
      return 'autosar.DataElement("%s","%s")'%(elem.name,elem.typeRef)
   
   
   def writeParameterInterfaceCode(self, portInterface,package):
      assert(isinstance(portInterface,autosar.portinterface.ParameterInterface))
      lines=[]
      if len(portInterface.dataElements)==1:
         dataElementCode=self.writeDataElementCode(portInterface.dataElements[0])
         lines.append('%s.createParameterInterface("%s",%s)'%(package.name,portInterface.name,dataElementCode))
      elif len(portInterface.dataElements)>1:
         raise NotImplementedError('more than one data element in an interface not yet supported')      
      return lines

   def writeClientServerInterfaceCode(self, portInterface,package):
      lines=[]
      lines.append('%s.createClientServerInterface("%s")'%(package.name,portInterface.name))
      return lines
