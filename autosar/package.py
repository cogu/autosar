import autosar.component
import autosar.behavior
import autosar.element
import autosar.portinterface
import autosar.datatype
import copy
import autosar.base
import re
from fractions import Fraction
import collections
import decimal

class Package(object):
   packageName = None
   def __init__(self, name, parent=None, role=None):
      self.name = name
      self.elements = []
      self.subPackages = []
      self.parent=parent
      self.role=role
      self.map={'elements':{}}
   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return None      

   def find(self,ref):
      if ref.startswith('/'): return self.parent.find(ref)
      ref = ref.partition('/')      
      name = ref[0]
      for package in self.subPackages:
         if package.name == name:
            if len(ref[2])>0:
               return package.find(ref[2])
            else:
               return package
      if name in self.map['elements']:
         elem=self.map['elements'][name]
         if len(ref[2])>0:
            return elem.find(ref[2])
         else:
            return elem
      return None
         
      # for elem in self.elements:
      #    if elem.name == name:
      #       if len(ref[2])>0:
      #          return elem.find(ref[2])
      #       else:
      #          return elem
      # return None
   
   def findall(self,ref):
      """
      experimental find-method that has some rudimentary support for globs.      
      """
      if ref is None: return None
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref = ref.partition('/')
      if ref[0]=='*' and len(ref[2])==0:
         result=list(self.elements)
         result.extend(self.subPackages)
      else:
         result=[]
         for item in (self.elements+self.subPackages):
            if item.name == ref[0] or ref[0]=='*':
               if len(ref[2])>0:
                  result.extend(item.findall(ref[2]))
               else:
                  result.append(item)
         if (len(result)==0) and ('*' in ref[0]):
            p = re.compile(ref[0].replace('*','.*'))
            for item in (self.elements+self.subPackages):
               m = p.match(item.name)
               if m is not None:
                  if len(ref[2])>0:
                     result.extend(item.findall(ref[2]))
                  else:
                     result.append(item)
      return result      
   
   def dir(self,ref=None,_prefix=''):
      if ref==None:
         return [_prefix+x.name for x in self.subPackages]+[_prefix+x.name for x in self.elements]      
      else:
         ref = ref.partition('/')
         result=self.find(ref[0])
         if result is not None:
            return result.dir(ref[2] if len(ref[2])>0 else None,_prefix+ref[0]+'/')
         else:
            return None
      
   
   def asdict(self):
      data={'type':self.__class__.__name__,'name':self.name,'elements':[],'subPackages':[]}
      for element in self.elements:
         if hasattr(element,'asdict'):            
            data['elements'].append(element.asdict())
         else:
            print(type(element))
      for subPackage in self.subPackages:         
         data['subPackages'].append(subPackage.asdict())
      if len(data['elements'])==0: del data['elements']
      if len(data['subPackages'])==0: del data['subPackages']
      return data
   
   def delete(self, ref):
      if ref is None: return
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref = ref.partition('/')
      for i,element in enumerate(self.elements):
         if element.name == ref[0]:
            if len(ref[2])>0:
               return element.delete(ref[2])
            else:
               del self.elements[i]
               break

   

   def createSenderReceiverInterface(self,name, dataElements=None, modeGroups=None, isService=False, adminData=None):
      """
      creates a new sender-receiver port interface. dataElements can either be a single instance of DataElement or a list of DataElements.
      The same applies to modeGroups. isService must be boolean
      """
      
      ws = self.rootWS()
      assert(ws is not None)

      portInterface = autosar.portinterface.SenderReceiverInterface(str(name), isService, adminData=adminData)
      if dataElements is not None:
         if isinstance(dataElements,collections.Iterable):
            for elem in dataElements:
               dataType=ws.find(elem.typeRef, role='DataType')
               if dataType is None:
                  raise ValueError('invalid type reference: '+elem.typeRef)            
               elem.typeRef=dataType.ref #normalize reference to data element
               portInterface.append(elem)
         elif isinstance(dataElements,autosar.portinterface.DataElement):         
            dataType=ws.find(dataElements.typeRef, role='DataType')
            if dataType is None:
               raise ValueError('invalid type reference: '+dataElements.typeRef)
            dataElements.typeRef=dataType.ref #normalize reference to data element
            portInterface.append(dataElements)
         else:
            raise ValueError("dataElements: expected autosar.portinterface.DataElement instance or list")
      if modeGroups is not None:
         if isinstance(modeGroups,collections.Iterable):
            for elem in modeGroups:
               portInterface.append(elem)
         elif isinstance(modeGroups,autosar.portinterface.ModeGroup):         
            portInterface.append(modeGroups)
         else:
            raise ValueError("dataElements: expected autosar.portinterface.DataElement instance or list")         
      self.append(portInterface)

   def createParameterInterface(self,name,dataElements=None,modeDeclarationGroups=None, isService=False, adminData=None):
      """
      creates a new parameter port interface. dataElements can either be a single instance of DataElement or a list of DataElements.
      The same applies to modeDeclarationGroups. isService must be boolean
      """
      ws = self.rootWS()
      assert(ws is not None)

      if isinstance(adminData, dict):
         adminDataObj=ws.createAdminData(adminData)
      else:
         adminDataObj = adminData
      if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
         raise ValueError("adminData must be of type dict or AdminData")
      portInterface = autosar.portinterface.ParameterInterface(str(name), adminData=adminDataObj)
      if isinstance(dataElements,collections.Iterable):
         for elem in dataElements:
            dataType=ws.find(elem.typeRef, role='DataType')
            if dataType is None:
               raise ValueError('invalid type reference: '+elem.typeRef)            
            elem.typeRef=dataType.ref #normalize reference to data element
            portInterface.append(elem)
      elif isinstance(dataElements,autosar.portinterface.DataElement):         
         dataType=ws.find(dataElements.typeRef, role='DataType')
         if dataType is None:
            raise ValueError('invalid type reference: '+dataElements.typeRef)
         dataElements.typeRef=dataType.ref #normalize reference to data element
         portInterface.append(dataElements)
      else:
         raise ValueError("dataElements: expected autosar.DataElement instance or list")
      self.append(portInterface)

         
   def createSubPackage(self, name, role=None):
      pkg = Package(name)
      self.append(pkg)
      if role is not None:
         ws = self.rootWS()
         assert(ws is not None)         
         ws.setRole(pkg.ref, role)
      
   
   
         
   def rootWS(self):
      if self.parent is None:
         return None
      else:
         return self.parent.root()
      
   def append(self,elem):
      """appends elem to the self.elements list"""
      if isinstance(elem,autosar.element.Element):         
         self.elements.append(elem)
         elem.parent=self
         self.map['elements'][elem.name]=elem
      elif isinstance(elem,Package):
        self.subPackages.append(elem)
        elem.parent=self
      else:
         raise ValueError('unexpected value type %s'%str(type(elem)))

   def update(self,other):
      """copies/clones each element from other into self.elements"""
      if type(self) == type(other):
         for otherElem in other.elements:            
            newElem=copy.deepcopy(otherElem)
            assert(newElem is not None)
            try:
               i=self.index('elements',otherElem.name)
               oldElem=self.elements[i]
               self.elements[i]=newElem
               oldElem.parent=None               
            except ValueError:
               self.elements.append(newElem)
            newElem.parent=self
      else:
         raise ValueError('cannot update from object of different type')

   def index(self,container,name):
      if container=='elements':
         lst=self.elements
      elif container=='subPackages':
         lst=self.subPackages
      else:
         raise KeyError("%s not in %s"%(container,self.__class__.__name__))
      return autosar.base.indexByName(lst,name)


   def createApplicationSoftwareComponent(self,swcName,behaviorName=None,implementationName=None,multipleInstance=False):
      """
      Creates a new ApplicationSoftwareComponent object and adds it to the package.
      It also creates an InternalBehavior object as well as an SwcImplementation object.
      
      """
      
      if behaviorName is None:
         behaviorName = str(swcName)+'_InternalBehavior'
      if implementationName is None:
         implementationName = str(swcName)+'_Implementation'
      swc = autosar.component.ApplicationSoftwareComponent(swcName,self)      
      internalBehavior = autosar.behavior.InternalBehavior(behaviorName,swc.ref,multipleInstance,self)
      implementation=autosar.component.SwcImplementation(implementationName,internalBehavior.ref,parent=self)
      swc.behavior=internalBehavior
      swc.implementation=implementation
      self.append(swc)
      self.append(internalBehavior)
      self.append(implementation)
      return swc
      

   def createModeDeclarationGroup(self, name, modeDeclarations, initialMode, adminData=None):
      """
      creates an instance of autosar.portinterface.ModeDeclarationGroup
      name: name of the ModeDeclarationGroup
      modeDeclarations: list of strings where each string is a mode name
      initialMode: string with name of the initial mode (must be one of the strings in modeDeclarations list)
      adminData: optional adminData object (use ws.createAdminData() as constructor)
      """
      ws = self.rootWS()
      assert(ws is not None)
      if isinstance(adminData, dict):
         adminDataObj=ws.createAdminData(adminData)
      else:
         adminDataObj = adminData
      if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
         raise ValueError("adminData must be of type dict or AdminData")
      group = autosar.portinterface.ModeDeclarationGroup(name,None,None,self,adminDataObj)
      for declarationName in modeDeclarations:
         item=autosar.portinterface.ModeDeclaration(declarationName,group)
         group.modeDeclarations.append(item)
         if declarationName == initialMode:
            group.initialModeRef = item.ref
      if group.initialModeRef is None:
         raise ValueError('initalMode "%s" not a valid modeDeclaration name'%initialMode)
      self.append(group)
      return group
         
   def createClientServerInterface(self, name, operations, errors=None, isService=False, adminData=None):
      """
      creates a new client server interface in current package
      name: name of the interface (string)
      operations: names of the operations in the interface (list of strings)
      errors: possible errors dict containing key-value pair where key is the name and value is the error code (must be integer)
      isService: True if this interface is a service interface (bool)
      adminData: optional admindata (dict or autosar.base.AdminData object)
      """
      portInterface = autosar.portinterface.ClientServerInterface(name, isService, self, adminData)
      for name in operations:
         portInterface.append(autosar.portinterface.Operation(name))      
      if errors is not None:
         if isinstance(errors, collections.Iterable):
            for error in errors:
               portInterface.append(error)
         else:            
            assert( isinstance(errors, autosar.portinterface.ApplicationError))
            portInterface.append(errors)
      self.append(portInterface)
      return portInterface

   def createSoftwareAddressMethod(self, name):
      item = autosar.portinterface.SoftwareAddressMethod(name)
      self.append(item)
      return item
      
   def createArrayDataType(self, name, typeRef, length, adminData=None):
      """creates an ArrayDataType and adds it to current package"""
      ws = self.rootWS()
      typeRefOrig=typeRef
      assert(ws is not None)
      if (not typeRef.startswith('/')) and (ws.roles['DataType'] is not None):
         typeRef=ws.roles['DataType']+'/'+typeRef      
      dataType = autosar.datatype.ArrayDataType(name, typeRef, length, adminData)
      self.append(dataType)
      return dataType

   def createIntegerDataType(self,name,min=None,max=None,valueTable=None,offset=None, scaling=None, unit=None, adminData=None, forceFloatScaling=False):
      """
      Helper method for creating integer datatypes in a package.
      In order to use this function you must have a subpackage present with role='CompuMethod'
      """
      semanticsPackage=None
      unitPackage=None
      ws=self.rootWS()
      assert(ws is not None)
      if ws.roles['CompuMethod'] is not None:
         semanticsPackage=ws.find(ws.roles['CompuMethod'])
         if semanticsPackage is None:
            raise RuntimeError("no package found with role='CompuMethod'")
      if ws.roles['Unit'] is not None:
         unitPackage=ws.find(ws.roles['Unit'])
         if unitPackage is None:
            raise RuntimeError("no package found with role='Unit'")
      
      if (valueTable is not None) and (min is not None) and (max is not None):
         #used for enumeration types using valueTables with explicit min and max
         compuMethod=autosar.CompuMethodConst(str(name),list(valueTable))
         if (semanticsPackage is not None):
            semanticsPackage.append(compuMethod)
            newType=autosar.datatype.IntegerDataType(name,min,max,compuMethodRef=compuMethod.ref, adminData=adminData)            
         else:
            raise RuntimeError("no package found with role='CompuMethod'")
      elif (valueTable is not None) and (min is None) and (max is None):
         #used for enumeration types using valueTables with implicitly calculated min and max
         compuMethod=autosar.CompuMethodConst(str(name),list(valueTable))
         if (semanticsPackage is not None):
            semanticsPackage.append(compuMethod)
            newType=autosar.datatype.IntegerDataType(name,0,len(valueTable)-1,compuMethodRef=compuMethod.ref, adminData=adminData)            
         else:
            raise RuntimeError("no package found with role='CompuMethod'")
      elif (min is not None) and (max is not None) and (offset is not None) and (scaling is not None):
         #creates an integer data type with rational scaling
         if forceFloatScaling:
            semanticElements=[{'offset':offset, 'numerator':scaling, 'denominator':1}]
         else:
            f=Fraction.from_float(scaling)
            if f.denominator > 1000: #use the float version in case its not a rational number
               semanticElements=[{'offset':offset, 'numerator':scaling, 'denominator':1}]
            else:
               semanticElements=[{'offset':offset, 'numerator':f.numerator, 'denominator':f.denominator}]
         compuMethod=autosar.datatype.CompuMethodRational(name,None,semanticElements)            
         if (semanticsPackage is not None):
            semanticsPackage.append(compuMethod)
            newType=autosar.datatype.IntegerDataType(name,min,max,compuMethodRef=compuMethod.ref, adminData=adminData)            
         else:
            raise RuntimeError("no package found with role='CompuMethod'")
         if unit is not None:
            if unitPackage is not None:
               unitElem = unitPackage.find(str(unit))
               if unitElem is None:
                  #create new unit if not found
                  unitElem = autosar.datatype.DataTypeUnitElement(unit,unit)
                  unitPackage.append(unitElem)
               compuMethod.unitRef=unitElem.ref
            else:
               raise RuntimeError("no package found with role='Unit'")
      elif (min is not None) and (max is not None):
         #creates a simple IntegerDataType
         newType=autosar.datatype.IntegerDataType(name,min,max, adminData=adminData)
      else:         
         raise NotImplementedError("not implemented")         
      self.append(newType)
      return newType

   def createRealDataType(self, name, minVal, maxVal, minValType='CLOSED', maxValType='CLOSED', hasNaN=False, encoding='SINGLE', adminData=None):
      """
      create a new instance of autosar.datatype.RealDataType and appends it to current package
      """
      dataType=autosar.datatype.RealDataType(name, minVal, maxVal, minValType, maxValType, hasNaN, encoding, self, adminData)
      self.append(dataType)
      return dataType
      
   def createRecordDataType(self, name, elements, adminData=None):
      """
      create a new instance of autosar.datatype.RecordDataType and appends it to current package
      """
      dataType=autosar.datatype.RecordDataType(name, elements, self, adminData)
      self.append(dataType)
      return dataType
      
   def createStringDataType(self, name, length, encoding='ISO-8859-1', adminData=None):
      """
      create a new instance of autosar.datatype.StringDataType and appends it to current package
      """
      dataType=autosar.datatype.StringDataType(name, length, encoding, self, adminData)
      self.append(dataType)
      return dataType

   def createBooleanDataType(self, name, adminData=None):
      """
      create a new instance of autosar.datatype.BooleanDataType and appends it to current package
      """
      dataType=autosar.datatype.BooleanDataType(name, self, adminData)
      self.append(dataType)
      return dataType

   def createConstant(self, name, typeRef, initValue, adminData=None):
      """
      create a new instance of autosar.constant.Constant and appends it to the current package
      """
      ws=self.rootWS()
      assert(ws is not None)
      dataType = ws.find(typeRef, role='DataType')
      value=None
      if dataType is None:
         raise ValueError('invalid reference:' + str(typeRef))
      if isinstance(dataType, autosar.datatype.IntegerDataType):
         if not isinstance(initValue, int):
            raise ValueError('initValue: expected type int, got '+str(type(initValue)))
         value=autosar.constant.IntegerValue(name, dataType.ref, initValue)         
      elif isinstance(dataType, autosar.datatype.RecordDataType):
         if isinstance(initValue, collections.Mapping) or isinstance(initValue, collections.Iterable):
            pass
         else:
            raise ValueError('initValue: expected type Mapping or Iterable, got '+str(type(initValue)))
         value=self._createRecordValue(ws, name, dataType, initValue)         
      elif isinstance(dataType, autosar.datatype.ArrayDataType):
         if isinstance(initValue, collections.Iterable):
            pass
         else:
            raise ValueError('initValue: expected type Iterable, got '+str(type(initValue)))
         value=self._createArrayValue(ws, name, dataType, initValue)         
      elif isinstance(dataType, autosar.datatype.BooleanDataType):
         if isinstance(initValue, bool):
            pass
         elif isinstance(initValue, str) or isinstance(initValue, int):
            initValue=bool(initValue)
         else:
            raise ValueError('initValue: expected type bool or str, got '+str(type(initValue)))
         value=autosar.constant.BooleanValue(name, dataType.ref, initValue)         
      elif isinstance(dataType, autosar.datatype.StringDataType):
         if isinstance(initValue, str):
            pass
         else:
            raise ValueError('initValue: expected type str, got '+str(type(initValue)))
         value=autosar.constant.StringValue(name, dataType.ref, initValue)         
      elif isinstance(dataType, autosar.datatype.RealDataType):
         if isinstance(initValue, float) or isinstance(initValue, decimal.Decimal) or isinstance(initValue, int):
            pass
         else:
            raise ValueError('initValue: expected type int, float or Decimal, got '+str(type(initValue)))
         value=autosar.constant.RealValue(name, dataType.ref, initValue)               
      else:
         raise ValueError('unrecognized type: '+str(type(dataType)))      
      assert(value is not None)
      constant = autosar.constant.Constant(name, value, adminData=adminData)
      self.append(constant)
      return constant
      
   def _createRecordValue(self, ws, name, dataType, initValue, parent=None):
      value = autosar.constant.RecordValue(name, dataType.ref, parent)
      if isinstance(initValue, collections.Mapping):
         for elem in dataType.elements:
            if elem.name in initValue:
               v = initValue[elem.name]               
               childType = ws.find(elem.typeRef, role='DataType')
               if childType is None:
                  raise ValueError('invalid reference: '+str(elem.typeRef))
               if isinstance(childType, autosar.datatype.IntegerDataType):
                  if not isinstance(v, int):
                     raise ValueError('v: expected type int, got '+str(type(v)))                     
                  value.elements.append(autosar.constant.IntegerValue(elem.name, childType.ref, v, value))
               elif isinstance(childType, autosar.datatype.RecordDataType):
                  if isinstance(v, collections.Mapping) or isinstance(v, collections.Iterable):
                     pass
                  else:
                     raise ValueError('v: expected type Mapping or Iterable, got '+str(type(v)))                     
                  value.elements.append(self._createRecordValue(ws, elem.name, childType, v, value))
               elif isinstance(childType, autosar.datatype.ArrayDataType):
                  if isinstance(v, collections.Iterable):
                     pass
                  else:
                     raise ValueError('v: expected type Iterable, got '+str(type(v)))                     
                  value.elements.append(self._createArrayValue(ws, elem.name, childType, v, value))
               elif isinstance(childType, autosar.datatype.BooleanDataType):
                  if isinstance(v, bool):
                     pass
                  elif isinstance(v, str) or isinstance(v, int):
                     v=bool(v)
                  else:
                     raise ValueError('v: expected type bool or str, got '+str(type(v)))                     
                  value.elements.append(autosar.constant.BooleanValue(elem.name, childType.ref, v, value))
               elif isinstance(childType, autosar.datatype.StringDataType):
                  if isinstance(v, str):
                     pass
                  else:
                     raise ValueError('v: expected type str, got '+str(type(v)))                     
                  value.elements.append(autosar.constant.StringValue(elem.name, childType.ref, v, value))
               elif isinstance(childType, autosar.datatype.RealDataType):
                  if isinstance(v, float) or isinstance(v, decimal.Decimal) or isinstance(v, int):
                     pass
                  else:
                     raise ValueError('v: expected type int, float or Decimal, got '+str(type(v)))                     
                  value.elements.append(autosar.constant.RealValue(elem.name, childType.ref, v, value))
               else:
                  raise ValueError('unrecognized type: '+str(type(childType)))
            else:
               raise ValueError('%s: missing initValue field: %s'%(name, elem.name))
      else:
         raise NotImplementedError(type(initValue))
      return value
            
   
   def _createArrayValue(self, ws, name, dataType, initValue, parent=None):
      value = autosar.constant.ArrayValue(name, dataType.ref, parent)
      childType = ws.find(dataType.typeRef, role='DataType')
      if childType is None:
         raise ValueError('invalid reference: '+str(elem.typeRef))      
      if isinstance(initValue, collections.Iterable):         
         for i in range(dataType.length):
            try:
               v=initValue[i]
            except IndexError:
               raise ValueError('%s: too few elements in initValue, expected %d items, got %d'%(name, int(dataType.length), len(initValue)))
            elemName='%s_%d'%(childType.name,i)
            if isinstance(childType, autosar.datatype.IntegerDataType):
               if not isinstance(v, int):
                  raise ValueError('v: expected type int, got '+str(type(v)))                     
               value.elements.append(autosar.constant.IntegerValue(elemName, childType.ref, v, value))
            elif isinstance(childType, autosar.datatype.RecordDataType):
               if isinstance(v, collections.Mapping) or isinstance(v, collections.Iterable):
                  pass
               else:
                  raise ValueError('v: expected type Mapping or Iterable, got '+str(type(v)))                     
               value.elements.append(self._createRecordValue(ws, elemName, childType, v, value))
            elif isinstance(childType, autosar.datatype.ArrayDataType):
               if isinstance(v, collections.Iterable):
                  pass
               else:
                  raise ValueError('v: expected type Iterable, got '+str(type(v)))                     
               value.elements.append(self._createArrayValue(ws, elemName, childType, v, value))
            elif isinstance(childType, autosar.datatype.BooleanDataType):
               if isinstance(v, bool):
                  pass
               elif isinstance(v, str) or isinstance(v, int):
                  v=bool(v)
               else:
                  raise ValueError('v: expected type bool or str, got '+str(type(v)))                     
               value.elements.append(autosar.constant.BooleanValue(elemName, childType.ref, v, value))
            elif isinstance(childType, autosar.datatype.StringDataType):
               if isinstance(v, str):
                  pass
               else:
                  raise ValueError('v: expected type str, got '+str(type(v)))                     
               value.elements.append(autosar.constant.StringValue(elemName, childType.ref, v, value))
            elif isinstance(childType, autosar.datatype.RealDataType):
               if isinstance(v, float) or isinstance(v, decimal.Decimal) or isinstance(v, int):
                  pass
               else:
                  raise ValueError('v: expected type int, float or Decimal, got '+str(type(v)))                     
               value.elements.append(autosar.constant.RealValue(elemName, childType.ref, v, value))
            else:
               raise ValueError('unrecognized type: '+str(type(childType)))            
      else:
         raise NotImplementedError(type(initValue))
      return value
   
   def createComplexDeviceDriverComponent(self,swcName,behaviorName=None,implementationName=None,multipleInstance=False):
      if behaviorName is None:
         behaviorName = str(swcName)+'_InternalBehavior'
      if implementationName is None:
         implementationName = str(swcName)+'_Implementation'
      swc=autosar.component.ComplexDeviceDriverComponent(swcName, parent=self)
      internalBehavior = autosar.behavior.InternalBehavior(behaviorName, swc.ref, multipleInstance, self)
      implementation=autosar.component.SwcImplementation(implementationName, internalBehavior.ref, parent=self)
      swc.behavior=internalBehavior
      swc.implementation=implementation
      self.append(swc)
      self.append(internalBehavior)
      self.append(implementation)
      return swc

   def createCompositionComponent(self, componentName, adminData=None):
      component = autosar.component.CompositionComponent(str(componentName), self)
      self.append(component)
      return component
      