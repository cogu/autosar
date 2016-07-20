from collections import namedtuple
from autosar.element import Element

from autosar.base import hasAdminData,parseAdminDataNode
import json

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
                     modeGroup = ModeGroup(xmlItem.find("./SHORT-NAME").text)
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
                     for xmlItem in xmlElem.find('SW-DATA-DEF-PROPS/SW-ADDR-METHOD-REF'):
                        dataElem.swAddrMethodRef.append(xmlItem.text)
                  portInterface.dataElements.append(dataElem)
            return portInterface
         
   def parseClientServerInterface(self,xmlRoot,rootProject=None,parent=None):
      assert(xmlRoot.tag=='CLIENT-SERVER-INTERFACE')
      xmlName = xmlRoot.find("./SHORT-NAME")
      if xmlName is not None:
         if self.version==3:
            portInterface = ClientServerInterface(xmlName.text)
            if xmlRoot.find("./IS-SERVICE").text == 'true': portInterface.isService = True
            for xmlOperation in xmlRoot.findall('./OPERATIONS/OPERATION-PROTOTYPE'):
               xmlOperationName = xmlOperation.find("./SHORT-NAME")
               if xmlOperationName is not None:
                  operation = Operation(xmlOperationName.text)
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
                  portInterface.applicationErrors.append(ApplicationError(name,errorCode))
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

class PortInterface(Element):
   def __init__(self,name,parent=None):
      super().__init__(name,parent)
      self.isService=False
      
class SenderReceiverInterface(PortInterface):
   def __init__(self,name):
      super().__init__(name)         
      self.dataElements=[]
      self.modeGroups=None
   
   def __iter__(self):
      return iter(self.dataElements)
   
   def dir(self):
      return [x.name for x in self.dataElements]         
   
   def asdict(self):
      retval = {'type': self.__class__.__name__, 'name': self.name, 'isService': self.isService, 'dataElements':[]}
      for elem in self.dataElements:
         retval['dataElements'].append(elem.asdict())
      if self.modeGroups is not None:
         retval['modeGroups']=[]
         for elem in self.modeGroups:
            retval['modeGroups'].append(elem.asdict())
      return retval
   
   def find(self,ref):
      ref = ref.partition('/')
      name = ref[0]
      for elem in self.dataElements:
         if elem.name==name:
            return elem      
      return None

   def append(self,elem):
      """
      adds elem to the self.dataElements list and sets elem.parent to self (the port interface)
      """
      if not isinstance(elem,DataElement):
         raise ValueError("expected elem variable to be of type DataElement")
      self.dataElements.append(elem)
      elem.parent=self
   

   

class ParameterInterface(PortInterface):
   def __init__(self,name):
      super().__init__(name)         
      self.dataElements=[]

   def asdict(self):
      retval = {'type': self.__class__.__name__, 'name': self.name, 'isService': self.isService, 'dataElements':[]}
      for elem in self.dataElements:
         retval['dataElements'].append(elem.asdict())
      return retval

   def append(self,elem):
      """
      adds elem to the self.dataElements list and sets elem.parent to self (the port interface)
      """
      if not isinstance(elem,DataElement):
         raise ValueError("expected elem variable to be of type DataElement")
      self.dataElements.append(elem)
      elem.parent=self      
   

class ClientServerInterface(PortInterface):
   def __init__(self,name):
      super().__init__(name)            
      self.operations=[]
      self.applicationErrors=[]
      self.adminData=None

   def asdict(self):
      retval = {'type': self.__class__.__name__, 'name': self.name, 'isService': self.isService, 'operations':[]}
      for elem in self.operations:
         retval['operations'].append(elem.asdict())
      if self.adminData is not None:
         retval['adminData']=self.adminData.asdict()
      if len(self.applicationErrors)>0:
         retval['applicationErrors']=[]
         for applicationError in self.applicationErrors:
            retval['applicationErrors'].append(applicationError.asdict())         
      return retval



class DataElement(object):
   def __init__(self,name,typeRef, isQueued=False, parent=None):
      self.name = name
      if isinstance(typeRef,str):
         self.typeRef=typeRef
      elif hasattr(typeRef,'ref'):
         assert(isinstance(typeRef.ref,str))
         self.typeRef=typeRef.ref
      else:
         raise ValueError("unsupported type for argument: typeRef")
      assert(isinstance(isQueued,bool))
      self.isQueued=isQueued
      self.adminData=None
      self.swAddrMethodRef=[]
      self.parent=parent
   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return '/%s'%self.name

   
   def asdict(self):
      data = {'type': self.__class__.__name__, 'name': self.name, 'isQueued': self.isQueued, 'typeRef': self.typeRef}
      data['adminData']=self.adminData.asdict() if self.adminData is not None else None
      if len(self.swAddrMethodRef)>0:
         data['swAddrMethodRef']=self.swAddrMethodRef
      return data
   

class ModeGroup(Element):
   def __init__(self,name):
      super().__init__(name)
      self.typeRef=None
   
   def asdict(self):
      return {'type': self.__class__.__name__, 'name':self.name, 'typeRef':self.typeRef}

class Operation(object):
   def __init__(self,name):
      self.name = name
      self.description = None
      self.arguments=[]
      self.errorRefs=[]

   def asdict(self):
      data = {'type': self.__class__.__name__, 'name':self.name, 'arguments':[]}
      for arg in self.arguments:
         data['arguments'].append(arg.asdict())
      if len(self.errorRefs)>0:
         data['errorRefs']=[]
         for errorRef in self.errorRefs:
            data['errorRefs'].append(errorRef)
      return data

class Argument(object):
   def __init__(self,name,typeRef,direction):
      self.name=name
      self.typeRef=typeRef
      if (direction != 'IN') and (direction != 'OUT') and (direction != 'INOUT'):
         raise ValueError('invalid value :%s'%direction)
      self.direction=direction
   def asdict(self):
      return {'type': self.__class__.__name__, 'name':self.name, 'typeRef':self.typeRef, 'direction': self.direction}

class ApplicationError(object):
   def __init__(self,name,errorCode):
      self.name=name
      self.errorCode=errorCode
   def asdict(self):
      return {'type': self.__class__.__name__, 'name':self.name,'errorCode':self.errorCode}

class SoftwareAddressMethod(Element):
   def __init__(self,name):
      super().__init__(name)

class ModeDeclarationGroup(Element):
   def __init__(self,name,initialModeRef=None,modeDeclarations=None):
      super().__init__(name)
      self.initialModeRef = initialModeRef
      self.modeDeclarations = modeDeclarations



#class PortInterfacePackage(Package):
#   def __init__(self):            
#      self.portInterfaces = []
#      super().__init__('PortInterface')
#   
#   def loadFromXML(self,root,version=3):
#      parser = PortInterfacePackageParser(self,version)
#      parser.loadFromXML(root)
#
#if __name__ == '__main__':
#   import xml.dom.minidom as minidom
#   import xml.etree.ElementTree as ElementTree
#   from arxml import removeNamespace,parseXMLFile
#   
#   xmlRoot = parseXMLFile('../../../../common/ic_types/davinci/PortInterfaces.arxml','http://autosar.org/3.0.2')
#   for package in xmlRoot.findall('.//AR-PACKAGE'):
#       name = package.find("./SHORT-NAME").text
#       if name=='PortInterface':       
#         pkg = PortInterfacePackage()
#         pkg.loadFromXML(package,3)
#         for portInterface in pkg.portInterfaces:            
#            print(json.dumps(portInterface.freeze(),indent=3))
         

