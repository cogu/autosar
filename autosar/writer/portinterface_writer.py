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
      typeElem = ws.find(elem.typeRef, role="DataType")
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
      typeElem = ws.find(elem.typeRef, role="DataType")					
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
      descLines = self.writeDescXML(operation)
      if descLines is not None:
         lines.extend(self.indent(descLines,1))
      if len(operation.arguments)>0:
         lines.append(self.indent('<ARGUMENTS>',1))
         for argument in operation.arguments:
            lines.append(self.indent('<%s>'%argument.tag(),2))
            lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%argument.name,3))
            typeElem = ws.find(argument.typeRef, role="DataType")					
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

#### CODE GENERATOTS ####

   def writeSenderReceiverInterfaceCode(self, portInterface, localvars):
      assert(isinstance(portInterface,autosar.portinterface.SenderReceiverInterface))
      lines=[]
      params=['"%s"'%portInterface.name]      
      if len(portInterface.dataElements)>1:
         raise NotImplementedError('more than one data element in an interface not yet supported')      
      elif len(portInterface.dataElements)==1:
         params.append(self.writeDataElementCode(portInterface.dataElements[0], localvars))
      
      if portInterface.modeGroups is not None:
         if len(portInterface.modeGroups)>1:
            raise NotImplementedError("more then one modegroup not yet supported")
         elif len(portInterface.modeGroups)==1:
            params.append('modeGroups='+self.writeModeGroupCode(portInterface.modeGroups[0], localvars))            
      
      if portInterface.isService:
         params.append('isService=True')
      if portInterface.adminData is not None:
         param = self.writeAdminDataCode(portInterface.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)
      lines.append('package.createSenderReceiverInterface(%s)'%(', '.join(params)))
      return lines
   
   def writeDataElementCode(self, elem, localvars):
      ws = elem.rootWS()
      assert(ws is not None)
      dataType = ws.find(elem.typeRef, role="DataType")
      if dataType is None:
         raise ValueError('invalid reference: '+elem.typeRef)
      #name
      params=[repr(elem.name)]
      #typeRef
      if ws.roles['DataType'] is not None:
         params.append(repr(dataType.name)) #use name only
      else:
         params.append(repr(dataType.ref)) #use full reference
      if elem.isQueued:
         params.append('True')
      if len(elem.swAddrMethodRefList)>1:
         raise NotImplementedError("data elements with more than one SoftwareAddressMethod reference not supported")
      if len(elem.swAddrMethodRefList)==1:
         params.append('softwareAddressMethodRef="%s"'%elem.swAddrMethodRefList[0])
      if elem.adminData is not None:
         param = self.writeAdminDataCode(elem.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)
      return 'autosar.DataElement(%s)'%(', '.join(params))   
   
   def writeModeGroupCode(self, modeGroup, localvars):
      ws = modeGroup.rootWS()
      assert(ws is not None)
      dataType = ws.find(modeGroup.typeRef, role="ModeDclrGroup")
      if dataType is None:
         raise ValueError('invalid reference: '+modeGroup.typeRef)
      params=['"%s"'%modeGroup.name, '"%s"'%dataType.ref]
      return 'autosar.ModeGroup(%s)'%(', '.join(params))      
   
   
   
   def writeParameterInterfaceCode(self, portInterface, localvars):
      assert(isinstance(portInterface,autosar.portinterface.ParameterInterface))
      lines=[]
      params=['"%s"'%portInterface.name]      
      if len(portInterface.dataElements)==1:
         code=self.writeDataElementCode(portInterface.dataElements[0], localvars)
         if (portInterface.dataElements[0].adminData is not None) or len(portInterface.dataElements[0].swAddrMethodRefList)>0:
            #this is going to be a long line, create separate dataElement variable
            lines.append('dataElement=%s'%code)
            params.append('dataElement')
         else:
            params.append(code)
      elif len(portInterface.dataElements)>1:
         raise NotImplementedError('more than one data element in an interface not yet supported')      
      if portInterface.isService:
         params.append('isService=True')      
      if portInterface.adminData is not None:
         param = self.writeAdminDataCode(portInterface.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)
      lines.append('package.createParameterInterface(%s)'%(', '.join(params)))
      return lines

   def writeClientServerInterfaceCode(self, portInterface, localvars):
      lines=[]
      ws = portInterface.rootWS()
      assert(ws is not None)
      params=['"%s"'%portInterface.name]
      params2=[]
      for operation in portInterface.operations:
         params2.append('"%s"'%operation.name)
      if len(params2)>3:
         lines.extend(self.writeListCode("operationsList",params2))
         params.append('operationsList')        
      else:
         params.append('['+', '.join(params2)+']')      
      params2=[]      
      for error in portInterface.applicationErrors:
         params2.append('autosar.ApplicationError("%s", %d)'%(error.name,error.errorCode))
      if len(params2)>1:
         lines.extend(self.writeListCode("errorsList",params2))
         params.append('errorsList')
      elif len(params2)==1:
         params.append(params2[0])
      
      if portInterface.isService:
         params.append('isService=True')
      if portInterface.adminData is not None:
         param = self.writeAdminDataCode(portInterface.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)
      lines.append('portInterface=package.createClientServerInterface(%s)'%(', '.join(params)))
      localvars['portInterface']=portInterface
      for operation in portInterface.operations:
         for argument in operation.arguments:
            methodLookup={"IN": "createInArgument", "OUT": "createOutArgument", "INOUT": "createInOutArgument"}
            dataType = ws.find(argument.typeRef)
            if dataType is None:
               raise ValueError("invalid reference: "+argument.typeRef)
            lines.append('portInterface["%s"].%s("%s", "%s")'%(operation.name, methodLookup[argument.direction], argument.name, dataType.name))
         params=[]
         if len(operation.errorRefs)>0:
            for ref in operation.errorRefs:
               error = ws.find(ref)
               if error is None:
                  raise ValueError("invalid reference: "+ref)
               params.append('"%s"'%error.name)
            lines.append('portInterface["%s"].possibleErrors = %s'%(operation.name, ', '.join(params)))
         desc,descAttr=self.writeDescCode(operation)
         if desc is not None:
            lines.append('portInterface["%s"].desc = "%s"'%(operation.name, desc))
         if descAttr is not None:
            lines.append('portInterface["%s"].descAttr = "%s"'%(operation.name, descAttr))
      return lines
   
   def writeSoftwareAddressMethodCode(self, method, localvars):
      lines=[]
      lines.append('%s.createSoftwareAddressMethod("%s")'%('package', method.name))
      return lines
   
   def writeModeDeclarationGroupCode(self, declarationGroup, localvars):
      lines=[]
      params=['"%s"'%declarationGroup.name]
      params2=[]
      for item in declarationGroup.modeDeclarations:
         params2.append('"%s"'%item.name)
      if len(params2)>6:
         lines.extend(self.writeListCode("modeDeclarationsList",params2))
         params.append('modeDeclarationsList')        
      else:
         params.append('['+', '.join(params2)+']')      
      assert(declarationGroup.initialModeRef is not None)
      tmp=autosar.base.splitRef(declarationGroup.initialModeRef)      
      params.append('"%s"'%tmp[-1])
         
      if declarationGroup.adminData is not None:
         param = self.writeAdminDataCode(declarationGroup.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)
         
      lines.append('package.createModeDeclarationGroup(%s)'%(', '.join(params)))
      return lines
   