#from collections import namedtuple
from autosar.element import Element



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
   
   @property
   def tag(self):
      return 'SENDER-RECEIVER-INTERFACE'

   

class ParameterInterface(PortInterface):
   @property
   def tag(self):
      return 'CALPRM-INTERFACE'

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
   @property
   def tag(self): return "DATA-ELEMENT-PROTOTYPE"
   
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




