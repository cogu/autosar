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
import sys

class Package(object):
   packageName = None
   def __init__(self, name, parent=None, role=None):
      self.name = name
      self.elements = []
      self.subPackages = []
      self.parent=parent
      self.role=role
      self.map={'elements':{}, 'packages':{}}

   def __getitem__(self,key):
      if isinstance(key,str):
         return self.find(key)
      else:
         raise ValueError('expected string')

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
      if name in self.map['packages']:
         package=self.map['packages'][name]
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

   def createParameterInterface(self,name,parameters=None,modeDeclarationGroups=None, isService=False, adminData=None):
      """
      Creates a new parameter port interface. parameter can either be a single instance of Parameter or a list of Parameters.
      The same applies to modeDeclarationGroups. isService must be boolean.
      In a previous version of this function the class DataElement was used instead of Parameter.
      In order to be backward compatible with old code, this method converts from old to new datatype internally
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
      if isinstance(parameters,collections.Iterable):
         for elem in parameters:
            dataType=ws.find(elem.typeRef, role='DataType')
            #normalize reference to data element
            if dataType is None:
               raise ValueError('invalid type reference: '+elem.typeRef)
            elem.typeRef=dataType.ref
            if isinstance(autosar.portinterface.DataElement):
               #convert into Parameter
               parameter = autosar.portinterface.Parameter(elem.name, elem.typeRef, elem.swAddressMethodRef, adminData=elem.adminData)
            else:
               parameter = elem
            portInterface.append(parameter)
      elif isinstance(parameters, autosar.portinterface.DataElement):
         dataType=ws.find(parameters.typeRef, role='DataType')
         #normalize reference to data element
         if dataType is None:
            raise ValueError('invalid type reference: '+parameters.typeRef)
         parameters.typeRef=dataType.ref
         parameter = autosar.portinterface.Parameter(parameters.name, parameters.typeRef,
                                                     parameters.swAddressMethodRef, adminData=parameters.adminData)
         portInterface.append(parameter)
      elif isinstance(parameters, autosar.portinterface.Parameter):
         dataType=ws.find(parameters.typeRef, role='DataType')
         #normalize reference to data element
         if dataType is None:
            raise ValueError('invalid type reference: '+parameters.typeRef)
         parameters.typeRef=dataType.ref
         portInterface.append(parameters)
      else:
         raise ValueError("dataElements: expected autosar.DataElement instance or list")
      self.append(portInterface)
      return portInterface

   def createModeSwitchInterface(self, name, modeGroup = None, isService=False, adminData=None):
      portInterface = autosar.portinterface.ModeSwitchInterface(name, isService, self, adminData)
      if modeGroup is not None:
         portInterface.modeGroup = modeGroup
         modeGroup.parent = portInterface
      self.append(portInterface)
      return portInterface

   def createSubPackage(self, name, role=None):
      pkg = Package(name)
      self.append(pkg)
      if role is not None:
         ws = self.rootWS()
         assert(ws is not None)
         ws.setRole(pkg.ref, role)
      return pkg

   def rootWS(self):
      if self.parent is None:
         return None
      else:
         return self.parent.rootWS()

   def append(self,elem):
      """appends elem to the self.elements list"""
      isNewElement = True
      if elem.name in self.map['elements']:
         isNewElement = False
         existingElem = self.map['elements'][elem.name]
         if type(elem) != type(existingElem):
            raise TypeError('Error: element %s %s already exists in package %s with different type from new element %s'%(str(type(existingElem)), existingElem.name, self.name, str(type(elem))))
         else:
            if elem != existingElem:
              raise ValueError('Error: element %s %s already exist in package %s using different definition'%(existingElem.name, str(type(existingElem)), self.name))
      if isNewElement:
         if isinstance(elem,autosar.element.Element):
            self.elements.append(elem)
            elem.parent=self
            self.map['elements'][elem.name]=elem
         elif isinstance(elem,Package):
           self.subPackages.append(elem)
           elem.parent=self
           self.map['packages'][elem.name]=elem
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
      ws = self.rootWS()
      assert(ws is not None)
      if ws.version < 4.0:
         # In AUTOSAR 3.x the internal behavior is a sub-element of the package.
         internalBehavior = autosar.behavior.InternalBehavior(behaviorName,swc.ref,multipleInstance,self)
      else:
         # In AUTOSAR 4.x the internal behavior is a sub-element of the swc.
         internalBehavior = autosar.behavior.SwcInternalBehavior(behaviorName,swc.ref,multipleInstance, swc)
      implementation=autosar.component.SwcImplementation(implementationName,internalBehavior.ref,parent=self)
      swc.behavior=internalBehavior
      swc.implementation=implementation
      self.append(swc)
      if ws.version < 4.0:
         # In AUTOSAR 3.x the internal behavior is a sub-element of the package.
         self.append(internalBehavior)
      self.append(implementation)
      return swc

   def createServiceComponent(self,swcName,behaviorName=None,implementationName=None,multipleInstance=False):
      """
      Creates a new ApplicationSoftwareComponent object and adds it to the package.
      It also creates an InternalBehavior object as well as an SwcImplementation object.

      """

      if behaviorName is None:
         behaviorName = str(swcName)+'_InternalBehavior'
      if implementationName is None:
         implementationName = str(swcName)+'_Implementation'
      swc = autosar.component.ServiceComponent(swcName,self)
      internalBehavior = autosar.behavior.InternalBehavior(behaviorName,swc.ref,multipleInstance,self)
      implementation=autosar.component.SwcImplementation(implementationName,internalBehavior.ref,parent=self)
      swc.behavior=internalBehavior
      swc.implementation=implementation
      self.append(swc)
      self.append(internalBehavior)
      self.append(implementation)
      return swc

   def createModeDeclarationGroup(self, name, modeDeclarations, initialMode, category=None, adminData=None):
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
      group = autosar.portinterface.ModeDeclarationGroup(name,None,None,category,self,adminDataObj)
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
      """
      AUTOSAR3:
         Creates an ArrayDataType and adds it to current package
      AUTOSAR4:
         Creates an ImplementationDataType and adds it to current package         
      """
      ws = self.rootWS()      
      assert(ws is not None)
      if (not typeRef.startswith('/')) and (ws.roles['DataType'] is not None):
         typeRef=ws.roles['DataType']+'/'+typeRef
      if ws.version >= 4.0:
         newType = autosar.datatype.ImplementationDataType(name, 'ARRAY', adminData=adminData)
         outerProps = autosar.base.SwDataDefPropsConditional(swCalibrationAccess='NOT-ACCESSIBLE')
         newType.variantProps = [outerProps]
         innerProps = autosar.base.SwDataDefPropsConditional(implementationTypeRef=typeRef)
         subElement = autosar.datatype.ImplementationDataTypeElement(name, 'TYPE_REFERENCE', length, variantProps=innerProps)
         newType.subElements.append(subElement)
      else:
         newType = autosar.datatype.ArrayDataType(name, typeRef, length, adminData)
      self.append(newType)
      return newType

   def createIntegerDataType(self,name,min=None,max=None,valueTable=None,offset=None, scaling=None, unit=None, baseTypeRef=None, adminData=None, forceFloatScaling=False, typeEmitter=None):
      """
      AUTOSAR3:
      Helper method for creating integer datatypes in a package.
      In order to use this function you must have a subpackage present with role='CompuMethod'.
      
      AUTOSAR4:
      Helper method for creating implementation datatypes or application datatypes.

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
         category = 'TEXTTABLE' if ws.version >= 4.0 else None
         compuMethod=autosar.CompuMethodConst(str(name),list(valueTable), category)
         if (semanticsPackage is not None):
            semanticsPackage.append(compuMethod)
            if ws.version >= 4.0:
               pass
            else:
               newType=autosar.datatype.IntegerDataType(name,min,max,compuMethodRef=compuMethod.ref, adminData=adminData)
         else:
            raise RuntimeError("no package found with role='CompuMethod'")
      elif (valueTable is not None) and (min is None) and (max is None):
         #used for enumeration types using valueTables with implicitly calculated min and max         
         category = 'TEXTTABLE' if ws.version >= 4.0 else None
         compuMethod=autosar.CompuMethodConst(str(name),list(valueTable), category)
         if (semanticsPackage is not None):
            semanticsPackage.append(compuMethod)
            if ws.version >= 4.0:
               if baseTypeRef is None:
                  raise ValueError('baseTypeRef argument must be given to this method')
               dataConstraint = self.createInternalDataConstraint(name+'_DataConstr', 0, len(valueTable)-1)
               newType = autosar.datatype.ImplementationDataType(name, 'VALUE')
               props = autosar.base.SwDataDefPropsConditional(baseTypeRef=baseTypeRef,
                                                              swCalibrationAccess='NOT-ACCESSIBLE',
                                                              compuMethodRef=compuMethod.ref,
                                                              dataConstraintRef=dataConstraint.ref)
               newType.variantProps = [props]
            else:
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
         else:
            unitElem = None
         if (semanticsPackage is not None):
            semanticsPackage.append(compuMethod)
            if ws.version >= 4.0:
#               if baseTypeRef is None:
#                  raise ValueError('baseTypeRef argument must be given to this method')
               dataConstraint = self.createInternalDataConstraint(name+'_DataConstr', min, max)
               if baseTypeRef is None:
                  #creates an application primitive data type by default
                  newType = autosar.datatype.ApplicationPrimitiveDataType(name, 'VALUE')
                  unitRef = unitElem.ref if unitElem is not None else None
                  props = autosar.base.SwDataDefPropsConditional(swCalibrationAccess='READ-ONLY',
                                                                 compuMethodRef=compuMethod.ref,
                                                                 dataConstraintRef=dataConstraint.ref,
                                                                 unitRef = unitRef)
               else:
                  #If baseTypeRef has been set, it creates an Implementation data type instead
                  newType = autosar.datatype.ImplementationDataType(name, 'VALUE')                  
                  props = autosar.base.SwDataDefPropsConditional(baseTypeRef=baseTypeRef,
                                                                 swCalibrationAccess='NOT-ACCESSIBLE',
                                                                 compuMethodRef=compuMethod.ref,
                                                                 dataConstraintRef=dataConstraint.ref)
               newType.variantProps = [props]
            else:               
               newType=autosar.datatype.IntegerDataType(name,min,max,compuMethodRef=compuMethod.ref, adminData=adminData)      
         else:
            raise RuntimeError("no package found with role='CompuMethod'")
      elif (min is not None) and (max is not None):
         #creates a simple IntegerDataType
         if ws.version >= 4.0:
            if baseTypeRef is None:
               raise ValueError('baseTypeRef argument must be given to this method')
            dataConstraint = self.createInternalDataConstraint(name+'_DataConstr', min, max)
            newType = autosar.datatype.ImplementationDataType(name, 'VALUE')
            props = autosar.base.SwDataDefPropsConditional(baseTypeRef=baseTypeRef,
                                                            swCalibrationAccess='NOT-ACCESSIBLE',
                                                            dataConstraintRef=dataConstraint.ref)
            newType.variantProps = [props]
         else:
            newType=autosar.datatype.IntegerDataType(name,min,max, adminData=adminData)
      else:
         raise NotImplementedError("not implemented")
      if typeEmitter is not None and isinstance(newType, autosar.datatype.ImplementationDataType):
         newType.typeEmitter = str(typeEmitter)
      self.append(newType)
      return newType

   def createRealDataType(self, name, minVal, maxVal, minValType='CLOSED', maxValType='CLOSED', hasNaN=False, encoding='SINGLE', baseTypeRef=None, adminData=None):
      """
      AUTOSAR 4: Creates a new ImplementationDataType
      AUTOSAR 3: Creates a new instance of autosar.datatype.RealDataType and appends it to current package
      """
      ws=self.rootWS()
      assert(ws is not None)
      if ws.version >= 4.0:
         if baseTypeRef is None:
            raise ValueError('baseTypeRef argument must be given to this method')
         if (minVal == '-INFINITE' or minVal == 'INFINITE'): minVal = '-INF'
         if (maxVal == 'INFINITE'): maxVal = 'INF'
         dataConstraint = self.createInternalDataConstraint(name+'_DataConstr', minVal, maxVal)
         newType = autosar.datatype.ImplementationDataType(name, 'VALUE')
         props = autosar.base.SwDataDefPropsConditional(baseTypeRef=baseTypeRef,
                                                            swCalibrationAccess='NOT-ACCESSIBLE',                                                              
                                                            dataConstraintRef=dataConstraint.ref)
         newType.variantProps = [props]
      else:         
         if (minVal == '-INFINITE' or '-INF'): minVal = 'INFINITE' #the missing '-' here is intentional. I know, AUTOSAR3 is weird.
         if (maxVal == 'INF'): maxVal = 'INFINITE'
         newType=autosar.datatype.RealDataType(name, minVal, maxVal, minValType, maxValType, hasNaN, encoding, self, adminData)
      self.append(newType)
      return newType

   def createRecordDataType(self, name, elements, swCalibrationAccess = None, adminData=None):
      """
      AUTOSAR3: Create a new instance of RecordDataType and appends it to current package
      AUTOSAR4: Creates a new ImplementationDataType and appends it to current package
      """
      ws = self.rootWS()
      assert(ws is not None)
      if ws.version < 4.0:
         dataType=autosar.datatype.RecordDataType(name, elements, self, adminData)
      else:
         if swCalibrationAccess is None:
            swCalibrationAccess = 'NOT-ACCESSIBLE'
         props = autosar.base.SwDataDefPropsConditional(swCalibrationAccess = swCalibrationAccess)
         dataType = autosar.datatype.ImplementationDataType(name, 'STRUCTURE', props, None, self, adminData)
         for element in elements:
            if not isinstance(element, tuple):
               raise ValueError('element must be a tuple')
            (elementName, elemTypeRef) = element
            elemType = ws.find(elemTypeRef, role='DataType')
            if elemType is None:
               raise ValueError('Unknown data type name: '+elemTypeRef)
            if isinstance(elemType, autosar.datatype.ImplementationDataType):
               props = autosar.base.SwDataDefPropsConditional(implementationTypeRef = elemType.ref)
            elif isinstance(elemType, autosar.datatype.SwBaseType):
               props = autosar.base.SwDataDefPropsConditional(baseTypeRef = elemType.ref)
            else:
               raise NotImplementedError(type(elemType))
            implementationDataTypeElement = autosar.datatype.ImplementationDataTypeElement(elementName, 'TYPE_REFERENCE', variantProps=props)
            dataType.subElements.append(implementationDataTypeElement)
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
      if ws.version < 4.0:
         self._createConstantV3(ws, name, dataType, initValue, adminData)
      else:
         self._createConstantV4(ws, name, dataType, initValue, adminData)

   def _createConstantV3(self, ws, name, dataType, initValue, adminData=None):
      """Creates an AUTOSAR 3 Constant"""
      if isinstance(dataType, autosar.datatype.IntegerDataType):
         if not isinstance(initValue, int):
            raise ValueError('initValue: expected type int, got '+str(type(initValue)))
         value=autosar.constant.IntegerValue(name, dataType.ref, initValue)
      elif isinstance(dataType, autosar.datatype.RecordDataType):
         if isinstance(initValue, collections.Mapping) or isinstance(initValue, collections.Iterable):
            pass
         else:
            raise ValueError('initValue: expected type Mapping or Iterable, got '+str(type(initValue)))
         value=self._createRecordValueV3(ws, name, dataType, initValue)
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

   def _createRecordValueV3(self, ws, name, dataType, initValue, parent=None):
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

   def _createConstantV4(self, ws, name, dataType, initValue, adminData=None):
      if isinstance(dataType, (autosar.datatype.ImplementationDataType, autosar.datatype.ApplicationPrimitiveDataType)):
         if dataType.category == 'VALUE':
            value = autosar.constant.NumericalValue(name, initValue)
         elif dataType.category == 'STRUCTURE':
           value = self._createRecordValueV4(ws, name, dataType, initValue)         
         else:
            raise NotImplementedError(dataType.category)
      assert(value is not None)
      constant = autosar.constant.Constant(name, value, parent=self, adminData=adminData)
      self.append(constant)
      return constant

   def _createRecordValueV4(self, ws, name, dataType, initValue, parent=None):
      value = autosar.constant.RecordValue(name, dataType.ref, parent)
      if isinstance(initValue, collections.Mapping):
         a = set() #datatype elements
         b = set() #initvalue elements
         for subElem in dataType.subElements:
            a.add(subElem.name)
         for key in initValue.keys():
            b.add(key)
         extra_keys = b-a
         for elem in extra_keys:
            print('Unknown name in initializer: %s.%s'%(name,elem), file=sys.stderr)
         for elem in dataType.subElements:
            if elem.name in initValue:
               v = initValue[elem.name]
               variantProps = elem.variantProps[0]
               if variantProps.implementationTypeRef is not None:
                  typeRef = variantProps.implementationTypeRef
               else:
                  raise NotImplementedError('could not deduce the type of element "%s"'%(elem.name))
               childType = ws.find(typeRef, role='DataType')
               if childType is None:
                  raise ValueError('Invalid reference: '+str(typeRef))
               if isinstance(childType, autosar.datatype.ImplementationDataType):
                  childProps = childType.variantProps[0]
                  if childProps.compuMethodRef is not None:
                     compuMethod = ws.find(childProps.compuMethodRef, role='CompuMethod')
                     if compuMethod is None:
                        raise ValueError('Invalid CompuMethod reference: '+childProps.compuMethodRef)
                     textValue = compuMethod.textValue(v)
                     if textValue is None:
                        raise ValueError('Could not find a text value that matches numerical value %s'%v )
                     value.elements.append(autosar.constant.TextValue(elem.name,textValue))
               else:
                  raise NotImplementedError(type(childType))
            else:
               raise ValueError('%s: missing initValue field: %s'%(name, elem.name))
      return value


   def createTextValueConstant(self, name, value):
      """AUTOSAR 4 text value constant"""
      constant = autosar.constant.Constant(name, None, self)
      constant.value = autosar.constant.TextValue(name, value, constant)
      self.append(constant)
      return constant

   def createNumericalValueConstant(self, name, value):
      """AUTOSAR 4 numerical value constant"""
      constant = autosar.constant.Constant(name, None, self)
      constant.value = autosar.constant.NumericalValue(name, value, constant)
      self.append(constant)
      return constant



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

   def createInternalDataConstraint(self, name, lowerLimit, upperLimit, lowerLimitType="CLOSED", upperLimitType="CLOSED"):
      ws = self.rootWS()
      assert(ws is not None)
      dataConstraintPackage = None
      if ws.roles['DataConstraint'] is None:
         raise RuntimeError("no package found with role='DataConstraint'")
      dataConstraintPackage=ws.find(ws.roles['DataConstraint'])
      rules=[]
      try:
         lowerLimit = int(lowerLimit)
      except ValueError:
         lowerLimit = str(lowerLimit)
      try:
         upperLimit = int(upperLimit)
      except ValueError:
         upperLimit = str(upperLimit)
      rules.append({'type': 'internalConstraint', 'lowerLimit':lowerLimit, 'upperLimit':upperLimit, 'lowerLimitType':lowerLimitType, 'upperLimitType':upperLimitType})
      constraint = autosar.datatype.DataConstraint(name, rules, self)
      dataConstraintPackage.append(constraint)
      return constraint

   def createSwBaseType(self, name, size, encoding=None, nativeDeclaration=None, adminData=None):
      """
      Creates a SwBaseType object
      """
      ws=self.rootWS()
      assert(ws is not None)

      if isinstance(adminData, dict):
         adminDataObj=ws.createAdminData(adminData)
      else:
         adminDataObj = adminData
      if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
         raise ValueError("adminData must be of type dict or AdminData")
      baseType = autosar.datatype.SwBaseType(name, size, encoding, nativeDeclaration, 'FIXED_LENGTH', self, adminData)
      self.append(baseType)
      return baseType
   
   def createBaseType(self, name, size, encoding=None, nativeDeclaration=None, adminData=None):
      """
      alias for createSwBaseType
      """
      return self.createSwBaseType(name, size, encoding, nativeDeclaration, adminData)


   def createImplementationDataTypeRef(self, name, typeRef, adminData = None):
      """
      Create a new implementation data type that is a reference to another implementation data type ref
      name: name of the new data type
      typeRef: reference to another implementation data type
      """
      ws=self.rootWS()
      assert(ws is not None)

      if isinstance(adminData, dict):
         adminDataObj=ws.createAdminData(adminData)
      else:
         adminDataObj = adminData
      if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
         raise ValueError("adminData must be of type dict or AdminData")
      variantProps = autosar.base.SwDataDefPropsConditional(implementationTypeRef = typeRef)
      implementationDataType = autosar.datatype.ImplementationDataType(name, 'TYPE_REFERENCE', variantProps, parent = self, adminData = adminData)
      self.append(implementationDataType)
      return implementationDataType