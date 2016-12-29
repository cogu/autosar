from autosar.element import Element
import collections
import autosar.base


class PortInterface(Element):
   def __init__(self, name, isService=False, parent=None, adminData=None):
      super().__init__(name,parent,adminData)
      self.isService=bool(isService)

   def __getitem__(self,key):
      if isinstance(key,str):
         return self.find(key)
      else:
         raise ValueError('expected string')
      
class SenderReceiverInterface(PortInterface):
   def __init__(self, name, isService=False, parent=None, adminData=None):
      super().__init__(name, isService, parent, adminData)
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
      if self.modeGroups is not None:
         for elem in self.modeGroups:
            if elem.name==name:
               return elem
         
      return None

   def append(self,elem):
      """
      adds elem to the self.dataElements list and sets elem.parent to self (the port interface)
      """
      if isinstance(elem,DataElement):
         self.dataElements.append(elem)
      elif isinstance(elem,ModeGroup):
         if self.modeGroups is None: self.modeGroups=[]
         self.modeGroups.append(elem)
      else:
         raise ValueError("expected elem variable to be of type DataElement")
      
      elem.parent=self
   
   def tag(self,version=None):
      return 'SENDER-RECEIVER-INTERFACE'

   

class ParameterInterface(PortInterface):
   def tag(self,version=None):
      return 'CALPRM-INTERFACE'

   def __init__(self, name, isService=False, parent=None, adminData=None):
      super().__init__(name, isService, parent, adminData)
      self.dataElements=[]

   def asdict(self):
      retval = {'type': self.__class__.__name__, 'name': self.name, 'isService': self.isService, 'dataElements':[]}
      for elem in self.dataElements:
         retval['dataElements'].append(elem.asdict())
      return retval

   def find(self,ref):
      ref = ref.partition('/')
      name = ref[0]
      for elem in self.dataElements:
         if elem.name==name:
            return elem

   def append(self,elem):
      """
      adds elem to the self.dataElements list and sets elem.parent to self (the port interface)
      """
      if not isinstance(elem,DataElement):
         raise ValueError("expected elem variable to be of type DataElement")
      self.dataElements.append(elem)
      elem.parent=self      
   

class ClientServerInterface(PortInterface):
   def __init__(self, name, isService=False, parent=None, adminData=None):
      super().__init__(name, isService, parent, adminData)
      self.operations=[]
      self.applicationErrors=[]
      

   def tag(self,version=None):
      return 'CLIENT-SERVER-INTERFACE'

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

   def find(self,ref):
      ref = ref.partition('/')
      name = ref[0]
      for elem in self.operations:
         if elem.name==name:
            return elem      
      for elem in self.applicationErrors:
         if elem.name==name:
            return elem      
      return None

   def append(self,elem):
      """
      adds elem to the self.operations or self.applicationErrors lists depending on type
      """
      if isinstance(elem, Operation):
         self.operations.append(elem)
      elif isinstance(elem, ApplicationError):
         self.applicationErrors.append(elem)
      else:
         raise ValueError("invalid type: %s"%(str(type(elem))))  
      elem.parent=self      



class DataElement(Element):
   def __init__(self,name, typeRef, isQueued=False, softwareAddressMethodRef=None, parent=None, adminData=None):
      super().__init__(name,parent,adminData)
      if isinstance(typeRef,str):
         self.typeRef=typeRef
      elif hasattr(typeRef,'ref'):
         assert(isinstance(typeRef.ref,str))
         self.typeRef=typeRef.ref
      else:
         raise ValueError("unsupported type for argument: typeRef")
      assert(isinstance(isQueued,bool))
      self.isQueued=isQueued
      self.swAddrMethodRefList=[]
      if softwareAddressMethodRef is not None:
         self.swAddrMethodRefList.append(str(softwareAddressMethodRef))
   def tag(self,version=None): return "DATA-ELEMENT-PROTOTYPE"
      
   def asdict(self):
      data = {'type': self.__class__.__name__, 'name': self.name, 'isQueued': self.isQueued, 'typeRef': self.typeRef}
      data['adminData']=self.adminData.asdict() if self.adminData is not None else None
      if len(self.swAddrMethodRefList)>0:
         data['swAddrMethodRef']=self.swAddrMethodRefList[:]
      return data

class ModeGroup(Element):
   def __init__(self, name, typeRef, parent=None, adminData=None):
      super().__init__(name, parent, adminData)
      self.typeRef=typeRef
   
   def tag(self,version=None): return "MODE-DECLARATION-GROUP-PROTOTYPE"
   
   def asdict(self):
      return {'type': self.__class__.__name__, 'name':self.name, 'typeRef':self.typeRef}

class Operation(Element):
   def __init__(self,name,parent=None):
      super().__init__(name,parent)      
      self.arguments=[]
      self.errorRefs=[]
   
   def tag(self,version=None):
      return 'OPERATION-PROTOTYPE'

   def asdict(self):
      data = {'type': self.__class__.__name__, 'name':self.name, 'arguments':[]}
      for arg in self.arguments:
         data['arguments'].append(arg.asdict())
      if len(self.errorRefs)>0:
         data['errorRefs']=[]
         for errorRef in self.errorRefs:
            data['errorRefs'].append(errorRef)
      return data
   
   def createOutArgument(self, name, typeRef):
      ws = self.rootWS()
      assert(ws is not None)
      dataType = ws.find(typeRef, role='DataType')
      if dataType is None:
         raise ValueError("invalid name or reference: "+typeRef)
      argument=Argument(name, dataType.ref, 'OUT')
      self.arguments.append(argument)
      return argument
   
   def createInOutArgument(self, name, typeRef):
      ws = self.rootWS()
      assert(ws is not None)
      dataType = ws.find(typeRef, role='DataType')
      if dataType is None:
         raise ValueError("invalid name or reference: "+typeRef)
      argument=Argument(name, dataType.ref, 'INOUT')
      self.arguments.append(argument)
      return argument

   def createInArgument(self, name, typeRef):
      ws = self.rootWS()
      assert(ws is not None)
      dataType = ws.find(typeRef, role='DataType')
      if dataType is None:
         raise ValueError("invalid name or reference: "+typeRef)
      argument=Argument(name, dataType.ref, 'IN')
      self.arguments.append(argument)
      return argument

   def append(self,elem):
      """
      adds elem to the self.arguments or self.errorRefs lists depending on type
      """
      if isinstance(elem, Argument):
         self.arguments.append(elem)
      elif isinstance(elem, str):
         self.errorRefs.append(elem)
      else:
         raise ValueError("invalid type: %s"%(str(type(elem))))
      elem.parent=self      
   
   
   @property 
   def possibleErrors(self):
      return None
   
   @possibleErrors.setter
   def possibleErrors(self, data):
      if self.parent is None:
         raise ValueError('cannot call this method without valid parent object')
      if isinstance(data, str):
         data=[data]         
      if isinstance(data, collections.Iterable):
         del self.errorRefs[:]
         for name in data:
            found=False
            for error in self.parent.applicationErrors:
               if error.name == name:
                  self.errorRefs.append(error.ref)
                  found=True
                  break
            if found==False:
               raise ValueError('invalid error name: "%s"'%name)
      else:
         raise ValueError("input argument must be string or iterrable")
   

class Argument(object):
   def __init__(self,name,typeRef,direction):
      self.name=name
      self.typeRef=typeRef
      if (direction != 'IN') and (direction != 'OUT') and (direction != 'INOUT'):
         raise ValueError('invalid value :%s'%direction)
      self.direction=direction
   
   def tag(self,version=None):
      return 'ARGUMENT-PROTOTYPE'      
   
   def asdict(self):
      return {'type': self.__class__.__name__, 'name':self.name, 'typeRef':self.typeRef, 'direction': self.direction}

class ApplicationError(Element):
   def __init__(self, name, errorCode, parent=None, adminData=None):
      super().__init__(name, parent, adminData)
      self.errorCode=int(errorCode)

   def tag(self,version=None):
      return 'APPLICATION-ERROR'

   def asdict(self):
      return {'type': self.__class__.__name__, 'name':self.name, 'errorCode':self.errorCode}



class SoftwareAddressMethod(Element):
   def __init__(self, name, parent=None, adminData=None):
      super().__init__(name, parent, adminData)
   
   def tag(self,version=None):
      return 'SW-ADDR-METHOD'

class ModeDeclarationGroup(Element):
   def __init__(self, name, initialModeRef=None, modeDeclarations=None, parent=None, adminData=None):
      super().__init__(name, parent, adminData)
      self.initialModeRef = initialModeRef
      if modeDeclarations is None:
         self.modeDeclarations = []
      else:
         self.modeDeclarations = list(modeDeclarations)   
   
   def tag(self, version=None): return "MODE-DECLARATION-GROUP"

   def find(self,ref):
      ref = ref.partition('/')
      name = ref[0]
      for elem in self.modeDeclarations:
         if elem.name==name:
            return elem      
      return None

class ModeDeclaration(Element):
   def __init__(self,name,parent=None):
      super().__init__(name,parent)
   
   def tag(self,version=None): return "MODE-DECLARATION"