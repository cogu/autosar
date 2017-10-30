from autosar.element import (Element, DataElement)
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

   def tag(self,version=None):
      return 'SENDER-RECEIVER-INTERFACE'
   
   def __init__(self, name, isService=False, serviceKind = None, parent=None, adminData=None):
      super().__init__(name, isService, parent, adminData)
      self.dataElements=[]
      self.modeGroups=None
      self.invalidationPolicies=[]
      self.serviceKind = serviceKind
   
   def __iter__(self):
      return iter(self.dataElements)
   
   def __eq__(self, other):
      if isinstance(other, self.__class__):
         if self.name == other.name and self.isService == other.isService and \
         self.adminData == other.adminData and len(self.dataElements) == len(other.dataElements):
            if (self.modeGroups is not None) and (other.modeGroups is not None) and len(self.modeGroups) == len(other.modeGroups):
               for i,elem in enumerate(self.modeGroups):
                  if elem != other.modeGroups[i]: return False
            return True
            for i,elem in enumerate(self.dataElements):
               if elem != other.dataElements[i]: return False
      return False
   
   def __ne__(self, other):
      return not (self == other)   
   
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
   
   def addInvalidationPolicy(self, invalidationPolicy):
      self.invalidationPolicies.append(invalidationPolicy)
         
   

class ParameterInterface(PortInterface):
   def tag(self,version=None):
      if version>=4.0:
         return 'PARAMETER-INTERFACE'
      else:
         return 'CALPRM-INTERFACE'
      
   def __init__(self, name, isService=False, parent=None, adminData=None):
      super().__init__(name, isService, parent, adminData)
      self.elements=[]

   def find(self,ref):
      ref = ref.partition('/')
      name = ref[0]
      for elem in self.elements:
         if elem.name==name:
            return elem

   def append(self,elem):
      """
      adds elem to the self.dataElements list and sets elem.parent to self (the port interface)
      """
      if not isinstance(elem,Parameter):
         raise ValueError("expected elem variable to be of type Parameter")
      self.elements.append(elem)
      elem.parent=self

class Parameter(Element):
   """
   Represents a <PARAMETER> element in AUTOSAR 4 or <CALPRM-ELEMENT-PROTOTYPE> in AUTOSAR 3
   """
   def tag(self, version):
         return "PARAMETER-DATA-PROTOTYPE" if version >=4.0 else "CALPRM-ELEMENT-PROTOTYPE"

   def __init__(self, name, typeRef = None, swAddressMethodRef=None, swCalibrationAccess=None, parent=None, adminData=None):
      super().__init__(name, parent, adminData)
      self.typeRef = typeRef
      self.swAddressMethodRef = swAddressMethodRef
      self.swCalibrationAccess = swCalibrationAccess

class ClientServerInterface(PortInterface):
   def __init__(self, name, isService=False, parent=None, adminData=None):
      super().__init__(name, isService, parent, adminData)
      self.operations=[]
      self.applicationErrors=[]
      self.serviceKind = None
      

   def tag(self,version=None):
      return 'CLIENT-SERVER-INTERFACE'


   def __eq__(self, other):
      if isinstance(other, self.__class__):
         if self.name == other.name and self.adminData == other.adminData and len(self.operations) == len(other.operations) and \
         len(self.applicationErrors) == len(other.applicationErrors):
            for i,operation in enumerate(self.operations):
               if operation != other.operations[i]: return False
            for i,applicationError in enumerate(self.applicationErrors):
               if applicationError != other.applicationErrors[i]: return False            
            return True
      return False
   
   def __ne__(self, other):
      return not (self == other)   


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

class ModeSwitchInterface(PortInterface):
   def tag(self, version): return 'MODE-SWITCH-INTERFACE'
   
   def __init__(self, name, isService=None, parent=None, adminData=None):
      super().__init__(name,isService, parent,adminData)
      self._modeGroup=None
      
   @property
   def modeGroup(self):
      return self._modeGroup
      
   @modeGroup.setter
   def modeGroup(self, value):
      if not isinstance(value, ModeGroup):
         raise ValueError('value must of ModeGroup type')
      self._modeGroup=value
      
   def find(self,ref):
      ref = ref.partition('/')
      name = ref[0]
      modeGroup = self.modeGroup
      if modeGroup is not None and modeGroup.name == name:
         return modeGroup
      return None


class ModeGroup(Element):
   def __init__(self, name, typeRef, parent=None, adminData=None):
      super().__init__(name, parent, adminData)
      self.typeRef=typeRef
   
   def tag(self,version=None):
      if version>=4.0:
         return "MODE-GROUP"
      else:
         return "MODE-DECLARATION-GROUP-PROTOTYPE"
   
   def asdict(self):
      return {'type': self.__class__.__name__, 'name':self.name, 'typeRef':self.typeRef}

   def __eq__(self, other):
      if isinstance(other, self.__class__):
         if self.name == other.name and self.adminData == other.adminData and self.typeRef == other.typeRef: return True
      return False
   
   def __ne__(self, other):
      return not (self == other)  

class Operation(Element):
   def tag(self,version=None):
      return 'CLIENT-SERVER-OPERATION' if version >=4.0 else 'OPERATION-PROTOTYPE'

   def __init__(self,name,parent=None):
      super().__init__(name,parent)      
      self.arguments=[]
      self.errorRefs=[]
   

   def __eq__(self, other):
      if isinstance(other, self.__class__):
         if self.name == other.name and self.adminData == other.adminData and len(self.arguments) == len(other.arguments) and \
         (len(self.errorRefs) == len(other.errorRefs)):
            for i,argument in enumerate(self.arguments):
               if argument != other.arguments[i]: return False
            for i,errorRef in enumerate(self.errorRefs):
               if errorRef != other.errorRefs[i]: return False
            return True
      return False
   
   def __ne__(self, other):
      return not (self == other)  

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
   

class Argument(Element):
   def tag(self,version=None):
      return 'ARGUMENT-DATA-PROTOTYPE' if version>=4.0 else 'ARGUMENT-PROTOTYPE'

   def __init__(self, name, typeRef, direction, parent=None, adminData=None):
      super().__init__(name, parent, adminData)
      self.typeRef=typeRef
      self.direction = direction
      self.swCalibrationAccess = None
      self.serverArgumentImplPolicy = None
   
   @property
   def direction(self):
      return self._direction
   
   @direction.setter
   def direction(self, value):
      if (value != 'IN') and (value != 'OUT') and (value != 'INOUT'):
         raise ValueError('invalid value :%s'%value)
      self._direction=value      
      
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
   def tag(self, version=None): return "MODE-DECLARATION-GROUP"
   
   def __init__(self, name, initialModeRef=None, modeDeclarations=None, parent=None, adminData=None):
      super().__init__(name, parent, adminData)
      self.initialModeRef = initialModeRef      
      if modeDeclarations is None:
         self.modeDeclarations = []
      else:
         self.modeDeclarations = list(modeDeclarations)
      self.category=None

   def find(self,ref):
      ref = ref.partition('/')
      name = ref[0]
      for elem in self.modeDeclarations:
         if elem.name==name:
            return elem      
      return None
   
   def __eq__(self, other):
      if isinstance(other, self.__class__):
         if self.name == other.name and self.initialModeRef == other.initialModeRef and \
         len(self.modeDeclarations) == len(other.modeDeclarations) and self.adminData == other.adminData:
            for i,left in enumerate(self.modeDeclarations):
               right = other.modeDeclarations[i]
               if left != right:
                  return False
            return True
      return False
   
   def __ne__(self, other):
      return not (self == other)

class ModeDeclaration(Element):
   def __init__(self,name,parent=None):
      super().__init__(name,parent)
   def __eq__(self, other):
      if isinstance(other, self.__class__):
         if self.name == other.name: return True
      return False
   
   def __ne__(self, other): return not (self == other)
   
   def tag(self,version=None): return "MODE-DECLARATION"

class InvalidationPolicy:
   valid_values = ['DONT-INVALIDATE', 'EXTERNAL-REPLACEMENT', 'KEEP', 'REPLACE']
   
   def tag(self, version): return 'INVALIDATION-POLICY'
   
   def __init__(self, dataElementRef, handleInvalid):
      self.dataElementRef = dataElementRef
      self.handleInvalid = handleInvalid
   
   @property
   def handleInvalid(self):
      return self._handleInvalid
   
   @handleInvalid.setter
   def handleInvalid(self, value):
      if value not in InvalidationPolicy.valid_values:
         raise ValueError('invalid value: %s'%value)
      self._handleInvalid = value
      