from autosar.base import hasAdminData,parseAdminDataNode
from autosar.portinterface import *

class PortInterfacePackageParser(object):
   def __init__(self,handler,version=3):
      if version == 3:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.handler=handler
   
   
   def loadFromXML(self,root):
      if self.version == 3:
         for elem in root.findall('./ELEMENTS/*'):
            if elem.tag=='SENDER-RECEIVER-INTERFACE':
               portInterface = self.parseSenderReceiverInterface(elem)
               if portInterface is not None:
                  self.handler.portInterfaces.append(portInterface)
   
   def parseSenderReceiverInterface(self,xmlRoot,rootProject=None,parent=None): 
         name = xmlRoot.find("./SHORT-NAME")
         if name is not None:
            if self.version==3:
               portInterface = SenderReceiverInterface(name.text)
               if hasAdminData(xmlRoot):
                  portInterface.adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))               
               if xmlRoot.find("./IS-SERVICE").text == 'true': portInterface.isService = True
               for xmlItem in xmlRoot.findall('./DATA-ELEMENTS/DATA-ELEMENT-PROTOTYPE'):
                  name = xmlItem.find("./SHORT-NAME")
                  if name is not None:
                     isQueued = True if xmlItem.find("./IS-QUEUED").text=='true' else False
                     typeRef=xmlItem.find("./TYPE-TREF").text
                     dataElem = DataElement(name.text,typeRef,isQueued,parent=portInterface)
                     portInterface.dataElements.append(dataElem)
               if xmlRoot.find('MODE-GROUPS') is not None:
                  portInterface.modeGroups=[]
                  for xmlItem in xmlRoot.findall('./MODE-GROUPS/MODE-DECLARATION-GROUP-PROTOTYPE'):
                     modeGroup = ModeGroup(xmlItem.find("./SHORT-NAME").text,portInterface)
                     modeGroup.typeRef = xmlItem.find("./TYPE-TREF").text
                     portInterface.modeGroups.append(modeGroup)
               return portInterface

   def parseParameterInterface(self,xmlRoot,rootProject=None,parent=None):
      assert(xmlRoot.tag=='CALPRM-INTERFACE')
      xmlName = xmlRoot.find("./SHORT-NAME")
      if xmlName is not None:
         if self.version==3:
            portInterface = ParameterInterface(xmlName.text)
            if xmlRoot.find("./IS-SERVICE").text == 'true': portInterface.isService = True
            for xmlElem in xmlRoot.findall('./CALPRM-ELEMENTS/CALPRM-ELEMENT-PROTOTYPE'):
               xmlElemName = xmlElem.find("./SHORT-NAME")
               if xmlElemName is not None:
                  typeRef=xmlElem.find("./TYPE-TREF").text
                  dataElem = DataElement(xmlElemName.text,typeRef,parent=portInterface)                  
                  if hasAdminData(xmlElem):
                     dataElem.adminData=parseAdminDataNode(xmlElem.find('ADMIN-DATA'))
                  if xmlElem.find('SW-DATA-DEF-PROPS'):
                     for xmlItem in xmlElem.findall('SW-DATA-DEF-PROPS/SW-ADDR-METHOD-REF'):
                        dataElem.swAddrMethodRefList.append(xmlItem.text)
                  portInterface.dataElements.append(dataElem)
            return portInterface
         
   def parseClientServerInterface(self,xmlRoot,rootProject=None,parent=None):
      assert(xmlRoot.tag=='CLIENT-SERVER-INTERFACE')
      xmlName = xmlRoot.find("./SHORT-NAME")
      if xmlName is not None:
         if self.version==3:
            portInterface = ClientServerInterface(xmlName.text)
            if hasAdminData(xmlRoot):
                  portInterface.adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
            if xmlRoot.find("./IS-SERVICE").text == 'true': portInterface.isService = True
            for xmlOperation in xmlRoot.findall('./OPERATIONS/OPERATION-PROTOTYPE'):
               xmlOperationName = xmlOperation.find("./SHORT-NAME")
               if xmlOperationName is not None:
                  operation = Operation(xmlOperationName.text,portInterface)
                  if xmlOperation.find('./ARGUMENTS') is not None:
                     for xmlArgument in xmlOperation.findall('./ARGUMENTS/ARGUMENT-PROTOTYPE'):
                        name=xmlArgument.find("./SHORT-NAME").text
                        typeRef = xmlArgument.find("./TYPE-TREF").text
                        direction = xmlArgument.find("./DIRECTION").text
                        operation.arguments.append(Argument(name,typeRef,direction))
                  if xmlOperation.find('./POSSIBLE-ERROR-REFS'):
                     for xmlErrorRef in xmlOperation.findall('./POSSIBLE-ERROR-REFS/POSSIBLE-ERROR-REF'):
                        operation.errorRefs.append(xmlErrorRef.text)            
                  portInterface.operations.append(operation)
            if xmlRoot.find('./POSSIBLE-ERRORS'):
               for xmlError in xmlRoot.findall('./POSSIBLE-ERRORS/APPLICATION-ERROR'):
                  name=xmlError.find("./SHORT-NAME").text
                  errorCode=xmlError.find("./ERROR-CODE").text
                  portInterface.applicationErrors.append(ApplicationError(name,errorCode,portInterface))
            return portInterface

class CEPParameterGroupPackageParser(object):
   def __init__(self,package,version=3):
      if version == 3:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.package=package
   def parseSWAddrMethod(self,xmlRoot,rootProject=None,parent=None):
      assert(xmlRoot.tag == 'SW-ADDR-METHOD')
      name = xmlRoot.find("./SHORT-NAME").text
      return SoftwareAddressMethod(name)
      
class ModeDeclarationGroupPackageParser(object):
   def __init__(self,package,version=3):
      if version == 3:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.package=package
      #self.elementParser=ElementParser(self.version)
   def parseModeDeclarationGroup(self,xmlRoot,rootProject=None,parent=None):
      assert(xmlRoot.tag == 'MODE-DECLARATION-GROUP')
      name = xmlRoot.find("./SHORT-NAME").text
      initialModeRef = None
      modeDeclarations = None
      if xmlRoot.find('./INITIAL-MODE-REF'):
         modeDeclarations = self.parseModeDeclarations(xmlRoot.find('./INITIAL-MODE-REF'),rootProject)
      if xmlRoot.find('./INITIAL-MODE-REF'):
         initialModeRef = xmlRoot.find('./INITIAL-MODE-REF').text
      modeDclrGroup = ModeDeclarationGroup(name,initialModeRef,modeDeclarations)
      if hasAdminData(xmlRoot):
         adminData = parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
         modeDclrGroup.adminData = adminData         
      return modeDclrGroup
   
   def parseModeDeclarations(self,xmlRoot,rootProject=None):
      assert(xmlRoot.tag=="MODE-DECLARATIONS")
      result = []
      for mode in xmlRoot.findall("./MODE-DECLARATION"):
         result.append(mode.find("./SHORT-NAME").text)
      return result
