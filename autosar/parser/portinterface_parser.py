from autosar.base import hasAdminData,parseAdminDataNode,parseTextNode
import autosar.portinterface
import autosar.base
import autosar.element
from autosar.parser.parser_base import ElementParser

class PortInterfacePackageParser(ElementParser):
   def __init__(self,version=3.0):
      self.version=version

      if self.version >= 3.0 and self.version < 4.0:
         self.switcher = {'SENDER-RECEIVER-INTERFACE': self.parseSenderReceiverInterface,
                          'CALPRM-INTERFACE': self.parseCalPrmInterface,
                          'CLIENT-SERVER-INTERFACE': self.parseClientServerInterface
         }
      elif self.version >= 4.0:
         self.switcher = {
            'SENDER-RECEIVER-INTERFACE': self.parseSenderReceiverInterface,
            'PARAMETER-INTERFACE': self.parseParameterInterface,
            'CLIENT-SERVER-INTERFACE': self.parseClientServerInterface,
            'MODE-SWITCH-INTERFACE': self.parseModeSwitchInterface
         }

   def getSupportedTags(self):
      return self.switcher.keys()

   def parseElement(self, xmlElement, parent = None):
      parseFunc = self.switcher.get(xmlElement.tag)
      if parseFunc is not None:
         return parseFunc(xmlElement,parent)
      else:
         return None

   def parseSenderReceiverInterface(self,xmlRoot,parent=None):
      (name, adminData, isService, serviceKind, xmlDataElements, xmlModeGroups, xmlInvalidationPolicys) = (None, None, False, None, None, None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'ADMIN-DATA':
            adminData = self.parseAdminDataNode(xmlElem)
         elif xmlElem.tag == 'IS-SERVICE':
            if self.parseTextNode(xmlElem) == 'true':
               isService = True
         elif xmlElem.tag == 'SERVICE-KIND':
            serviceKind = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'DATA-ELEMENTS':
            xmlDataElements = xmlElem
         elif xmlElem.tag == 'INVALIDATION-POLICYS':
            xmlInvalidationPolicys = xmlElem
         elif xmlElem.tag == 'MODE-GROUPS':
            xmlModeGroups = xmlElem
         else:
            raise NotImplementedError(xmlElem.tag)
         
      if (name is not None) and (xmlDataElements is not None):
         portInterface = autosar.portinterface.SenderReceiverInterface(name, isService, serviceKind, parent, adminData)
         if self.version >= 4.0:
            elemParser = self.parseVariableDataPrototype
            dataElemTag = 'VARIABLE-DATA-PROTOTYPE'  
         else:
            elemParser = self.parseDataElement
            dataElemTag = 'DATA-ELEMENT-PROTOTYPE'
         for xmlChild in xmlDataElements.findall('./*'):
            if xmlChild.tag == dataElemTag:
               dataElem = elemParser(xmlChild, portInterface)
               portInterface.dataElements.append(dataElem)               
            else:
               raise NotImplementedError(xmlChild.tag)
         if self.version >= 4.0 and xmlInvalidationPolicys is not None:
            for xmlChild in xmlInvalidationPolicys.findall('./*'):
               if xmlChild.tag == 'INVALIDATION-POLICY':                  
                  invalidationPolicy = self._parseInvalidationPolicy(xmlChild)
                  portInterface.addInvalidationPolicy(invalidationPolicy)
               else:
                  raise NotImplementedError(xmlChild.tag)
         if self.version < 4.0 and xmlModeGroups is not None:
            portInterface.modeGroups=[]
            for xmlItem in xmlModeGroups.findall('./MODE-DECLARATION-GROUP-PROTOTYPE'):
               modeGroup = autosar.portinterface.ModeGroup(xmlItem.find("./SHORT-NAME").text,xmlItem.find("./TYPE-TREF").text,portInterface)                     
               portInterface.modeGroups.append(modeGroup)
         return portInterface
   
   def parseDataElement(self, xmlRoot, parent):
      assert(xmlRoot.tag == 'DATA-ELEMENT-PROTOTYPE')
      (name, typeRef, isQueued) = (None, None, False)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'TYPE-TREF':
            typeRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'IS-QUEUED':
            isQueued = True if self.parseTextNode(xmlElem) == 'true' else False            
         else:
            raise NotImplementedError(xmlElem.tag)
      if (name is not None) and (typeRef is not None):
         return autosar.element.DataElement(name, typeRef, isQueued, parent=parent)
      else:
         raise RuntimeError('SHORT-NAME and TYPE-TREF must not be None')

      
   def _parseInvalidationPolicy(self, xmlRoot):
      (dataElementRef, handleInvalid) = (None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'DATA-ELEMENT-REF':
            dataElementRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'HANDLE-INVALID':
            handleInvalid = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (dataElementRef is not None) and (handleInvalid is not None):
         return autosar.portinterface.InvalidationPolicy(dataElementRef, handleInvalid)
      else:
         raise RuntimeError('DATA-ELEMENT-REF and HANDLE-INVALID must not be None')
         
         # name = xmlRoot.find("./SHORT-NAME")
         # if name is not None:            
         #    portInterface = autosar.portinterface.SenderReceiverInterface(name.text)
         #    if hasAdminData(xmlRoot):
         #       portInterface.adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
         #    if xmlRoot.find("./IS-SERVICE").text == 'true': portInterface.isService = True
         #    for xmlItem in xmlRoot.findall('./DATA-ELEMENTS/DATA-ELEMENT-PROTOTYPE'):
         #       name = xmlItem.find("./SHORT-NAME")
         #       if name is not None:
         #          isQueued = True if xmlItem.find("./IS-QUEUED").text=='true' else False
         #          typeRef=xmlItem.find("./TYPE-TREF").text
         #          dataElem = autosar.portinterface.DataElement(name.text,typeRef,isQueued,parent=portInterface)
         #          portInterface.dataElements.append(dataElem)
         #    if xmlRoot.find('MODE-GROUPS') is not None:
         #       portInterface.modeGroups=[]
         #       for xmlItem in xmlRoot.findall('./MODE-GROUPS/MODE-DECLARATION-GROUP-PROTOTYPE'):
         #          modeGroup = autosar.portinterface.ModeGroup(xmlItem.find("./SHORT-NAME").text,xmlItem.find("./TYPE-TREF").text,portInterface)
         #          portInterface.modeGroups.append(modeGroup)
         #    return portInterface

   def parseCalPrmInterface(self,xmlRoot,parent=None):
      assert(xmlRoot.tag=='CALPRM-INTERFACE')
      xmlName = xmlRoot.find("./SHORT-NAME")
      if xmlName is not None:         
         portInterface = autosar.portinterface.ParameterInterface(xmlName.text)
         if xmlRoot.find("./IS-SERVICE").text == 'true': portInterface.isService = True
         for xmlElem in xmlRoot.findall('./CALPRM-ELEMENTS/CALPRM-ELEMENT-PROTOTYPE'):
            xmlElemName = xmlElem.find("./SHORT-NAME")
            if xmlElemName is not None:
               typeRef=xmlElem.find("./TYPE-TREF").text
               parameter = autosar.portinterface.Parameter(xmlElemName.text,typeRef,parent=portInterface)
               if hasAdminData(xmlElem):
                  parameter.adminData=parseAdminDataNode(xmlElem.find('ADMIN-DATA'))
               if xmlElem.find('SW-DATA-DEF-PROPS'):
                  for xmlItem in xmlElem.findall('SW-DATA-DEF-PROPS/SW-ADDR-METHOD-REF'):
                     parameter.swAddressMethodRef = self.parseTextNode(xmlItem)
               portInterface.elements.append(parameter)
         return portInterface

   def parseClientServerInterface(self,xmlRoot,parent=None):
      assert(xmlRoot.tag=='CLIENT-SERVER-INTERFACE')
      name = self.parseTextNode(xmlRoot.find('SHORT-NAME'))
      if name is not None:            
            portInterface = autosar.portinterface.ClientServerInterface(name)            
            if hasAdminData(xmlRoot):
                  portInterface.adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
            for xmlElem in xmlRoot.findall('./*'):
               if (xmlElem.tag == 'SHORT-NAME') or (xmlElem.tag == 'ADMIN-DATA'):
                  continue
               elif xmlElem.tag == 'IS-SERVICE':
                  if self.parseTextNode(xmlElem) == 'true':
                     portInterface.isService = True
               elif xmlElem.tag == 'OPERATIONS':
                  for xmlChildItem in xmlElem.findall('./*'):
                     if (self.version < 4.0 and xmlChildItem.tag == 'OPERATION-PROTOTYPE') or (self.version >= 4.0 and xmlChildItem.tag == 'CLIENT-SERVER-OPERATION'):
                        operation = self._parseOperationPrototype(xmlChildItem, portInterface)
                        portInterface.operations.append(operation)
                     else:
                        raise NotImplementedError(xmlChildItem.tag)
               elif xmlElem.tag == 'POSSIBLE-ERRORS':
                  for xmlError in xmlElem.findall('APPLICATION-ERROR'):
                     applicationError = self._parseApplicationError(xmlError, portInterface)
                     portInterface.applicationErrors.append(applicationError)
               elif xmlElem.tag == 'SERVICE-KIND':
                  portInterface.serviceKind = self.parseTextNode(xmlElem)
               else:
                  raise NotImplementedError(xmlElem.tag)
            return portInterface
   
   def parseParameterInterface(self,xmlRoot,parent=None):
      (name, adminData, isService, xmlParameters) = (None, None, False, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'ADMIN-DATA':
            adminData = self.parseAdminDataNode(xmlElem)
         elif xmlElem.tag == 'IS-SERVICE':
            if self.parseTextNode(xmlElem) == 'true':
               isService = True
         elif xmlElem.tag == 'PARAMETERS':
            xmlParameters = xmlElem
         else:
            raise NotImplementedError(xmlElem.tag)
      
      if (name is not None) and (xmlParameters is not None):
         portInterface = autosar.portinterface.ParameterInterface(name, isService, parent, adminData)
         for xmlChild in xmlParameters.findall('./*'):
            if xmlChild.tag == 'PARAMETER-DATA-PROTOTYPE':
               parameter = self._parseParameterDataPrototype(xmlChild, portInterface)
               portInterface.append(parameter)
            else:
               raise NotImplementedError(xmlChild.tag)
         return portInterface


   def parseModeSwitchInterface(self,xmlRoot,parent=None):
      (name, adminData, desc, isService, xmlModeGroup) = (None, None, None, False, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'ADMIN-DATA':
            adminData = self.parseAdminDataNode(xmlElem)
         elif xmlElem.tag == 'IS-SERVICE':
            if self.parseTextNode(xmlElem) == 'true':
               isService = True
         elif xmlElem.tag == 'MODE-GROUP':
            xmlModeGroup = xmlElem
         else:
            raise NotImplementedError(xmlElem.tag)
      
      if (name is not None) and (xmlModeGroup is not None):
         portInterface = autosar.portinterface.ModeSwitchInterface(name, isService, parent, adminData)
         portInterface.modeGroup=self._parseModeGroup(xmlModeGroup, portInterface)
         return portInterface
   
   def _parseModeGroup(self, xmlModeGroup, parent):
      if self.version>=4.0:
         assert(xmlModeGroup.tag == "MODE-GROUP")
      else:
         assert(xmlModeGroup.tag == "MODE-DECLARATION-GROUP-PROTOTYPE")
      name = self.parseTextNode(xmlModeGroup.find('SHORT-NAME'))
      typeRef = self.parseTextNode(xmlModeGroup.find('TYPE-TREF'))
      return autosar.portinterface.ModeGroup(name, typeRef, parent)

   def _parseOperationPrototype(self, xmlOperation, parent):
      (name, xmlDesc, xmlArguments, xmlPossibleErrorRefs) = (None, None, None, None)
      for xmlElem in xmlOperation.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'DESC':
            xmlDesc = xmlElem
         elif xmlElem.tag == 'ARGUMENTS':
            xmlArguments = xmlElem
         elif xmlElem.tag == 'POSSIBLE-ERROR-REFS':
            xmlPossibleErrorRefs = xmlElem
         else:
            raise NotImplementedError(xmlElem.tag)
      
      if name is not None:
         operation = autosar.portinterface.Operation(name, parent)
         argumentTag = 'ARGUMENT-DATA-PROTOTYPE' if self.version >= 4.0 else 'ARGUMENT-PROTOTYPE'
         if xmlDesc is not None:
            self.parseDesc(xmlOperation,operation)         
         if xmlArguments is not None:
            for xmlChild in xmlArguments.findall('./*'):            
               if xmlChild.tag == argumentTag:
                  if self.version >= 4.0:
                     argument = self._parseOperationArgumentV4(xmlChild, operation)
                  else:
                     argument = self._parseOperationArgumentV3(xmlChild, operation)
                  operation.arguments.append(argument)
               else:
                  raise NotImplementedError(xmlChild.tag)
         if xmlPossibleErrorRefs is not None:
            for xmlChild in xmlPossibleErrorRefs.findall('./*'):
               if xmlChild.tag == 'POSSIBLE-ERROR-REF':
                  operation.errorRefs.append(self.parseTextNode(xmlChild))
               else:
                  raise NotImplementedError(xmlChild.tag)
         return operation
         
   def _parseOperationArgumentV3(self, xmlArgument, parent):
      (name, typeRef, direction) = (None, None, None)
      for xmlElem in xmlArgument.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'TYPE-TREF':
            typeRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'DIRECTION':
            direction = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (name is not None) and (typeRef is not None) and (direction is not None):
         return autosar.portinterface.Argument(name, typeRef, direction)
      else:
         raise RuntimeError('SHORT-NAME, TYPE-TREF and DIRECTION must have valid values')

   def _parseOperationArgumentV4(self, xmlArgument, parent):
      (name, typeRef, direction, props_variants, serverArgumentImplPolicy) = (None, None, None, None, None)
      for xmlElem in xmlArgument.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'TYPE-TREF':
            typeRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'DIRECTION':
            direction = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
            props_variants = self.parseSwDataDefProps(xmlElem)
         elif xmlElem.tag == 'SERVER-ARGUMENT-IMPL-POLICY':
            serverArgumentImplPolicy=self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (name is not None) and (typeRef is not None) and (direction is not None):
         argument = autosar.portinterface.Argument(name, typeRef, direction)
         if props_variants is not None:            
            argument.swCalibrationAccess = props_variants[0].swCalibrationAccess
         return argument
      else:
         raise RuntimeError('SHORT-NAME, TYPE-TREF and DIRECTION must have valid values')
      
   def _parseApplicationError(self, xmlElem, parent):
      name=self.parseTextNode(xmlElem.find("./SHORT-NAME"))
      errorCode=self.parseTextNode(xmlElem.find("./ERROR-CODE"))
      return autosar.portinterface.ApplicationError(name, errorCode, parent)

   def _parseParameterDataPrototype(self, xmlElem, parent):
      (name, adminData, typeRef, props_variants) = (None, None, None, None)
      for xmlElem in xmlElem.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'ADMIN-DATA':
            adminData = self.parseAdminDataNode(xmlElem)
         elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
            props_variants = self.parseSwDataDefProps(xmlElem)         
         elif xmlElem.tag == 'TYPE-TREF':
            typeRef = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      
      if (name is not None) and (typeRef is not None):
         parameter = autosar.portinterface.Parameter(name, typeRef, parent=parent, adminData=adminData)
         if props_variants is not None:
            parameter.swCalibrationAccess = props_variants[0].swCalibrationAccess
            parameter.swAddressMethodRef = props_variants[0].swAddressMethodRef            
         return parameter
      

class SoftwareAddressMethodParser(ElementParser):
   def __init__(self,version=3.0):
      self.version=version

   def getSupportedTags(self):
      return ['SW-ADDR-METHOD']

   def parseElement(self, xmlElement, parent = None):
      if xmlElement.tag == 'SW-ADDR-METHOD':
         return self.parseSWAddrMethod(xmlElement, parent)
      else:
         return None

   def parseSWAddrMethod(self,xmlRoot,rootProject=None,parent=None):
      assert(xmlRoot.tag == 'SW-ADDR-METHOD')
      name = xmlRoot.find("./SHORT-NAME").text
      return autosar.portinterface.SoftwareAddressMethod(name)

class ModeDeclarationGroupPackageParser(ElementParser):
   def __init__(self,version=3):
      self.version=version

      if self.version >= 3.0 and self.version < 4.0:
         self.switcher = {'MODE-DECLARATION-GROUP': self.parseModeDeclarationGroup,
                          'MODE-DECLARATIONS': self.parseModeDeclarations
         }
      elif self.version >= 4.0:
         self.switcher = {
            'MODE-DECLARATION-GROUP': self.parseModeDeclarationGroup
         }

   def getSupportedTags(self):
      return self.switcher.keys()

   def parseElement(self, xmlElement, parent = None):
      parseFunc = self.switcher.get(xmlElement.tag)
      if parseFunc is not None:
         return parseFunc(xmlElement,parent)
      else:
         return None


   def parseModeDeclarationGroup(self,xmlRoot,rootProject=None,parent=None):
      assert(xmlRoot.tag == 'MODE-DECLARATION-GROUP')
      name = self.parseTextNode(xmlRoot.find("./SHORT-NAME"))
      category = self.parseTextNode(xmlRoot.find("./CATEGORY"))
      initialModeRef = self.parseTextNode(xmlRoot.find('./INITIAL-MODE-REF'))
      modeDclrGroup = autosar.portinterface.ModeDeclarationGroup(name,initialModeRef,None,parent)
      if xmlRoot.find('./MODE-DECLARATIONS') is not None:
         self.parseModeDeclarations(xmlRoot.find('./MODE-DECLARATIONS'), modeDclrGroup)
      if hasAdminData(xmlRoot):
         adminData = self.parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
         modeDclrGroup.adminData = adminData
      if category is not None:
         modeDclrGroup.category = category
      return modeDclrGroup

   def parseModeDeclarations(self,xmlRoot,parent):
      assert(xmlRoot.tag=="MODE-DECLARATIONS")
      assert(isinstance(parent, autosar.portinterface.ModeDeclarationGroup))
      result = []
      for mode in xmlRoot.findall("./MODE-DECLARATION"):
         parent.modeDeclarations.append(autosar.portinterface.ModeDeclaration(parseTextNode(mode.find("./SHORT-NAME")), parent))
      return result
