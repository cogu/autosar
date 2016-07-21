from autosar.package import Package
from autosar.element import Element
from autosar.base import parseXMLFile,splitref,parseTextNode
import math
import json

#RecordTypeElement=namedtuple('RecordTypeElement',['name','typeRef'])
#CompuConstElement=namedtuple('CompuConstElement','minvalue maxvalue textvalue')
#CompuRationalElement=namedtuple('CompuRationalElement','offset numerator denominator')
#DataTypeUnitElement = namedtuple('DataTypeUnitElement','name displayName')

class ConstElement(object):
   def asdict(self):
      data={'type': self.__class__.__name__}
      data.update(self.__dict__)
      return data


class RecordTypeElement(ConstElement):
   def __init__(self,name,typeRef):
      self.name=name
      self.typeRef=typeRef

class CompuConstElement(ConstElement):
   def __init__(self,minvalue,maxvalue,textvalue):
      self.minval=minvalue
      self.maxval=maxvalue
      self.textval=textvalue

class CompuRationalElement(ConstElement):
   def __init__(self,offset,numerator,denominator):
      self.offset=offset
      self.numerator=numerator
      self.denominator=denominator

class DataTypeUnitElement(Element):
   def __init__(self,name,displayName):
      super().__init__(name)
      self.displayName=displayName

class DataType(Element):
   name = None
   def __init__(self,name):
      super().__init__(name)      


class IntegerDataType(DataType):
   @property
   def tag(self): return 'INTEGER-TYPE'
   def __init__(self,name,minval=0,maxval=0,compuMethodRef=None):
      super().__init__(name)
      self.minval = minval
      self.maxval = maxval
      if isinstance(compuMethodRef,str):
         self.compuMethodRef=compuMethodRef
      elif hasattr(compuMethodRef,'ref'):
         self.compuMethodRef=compuMethodRef.ref
      else:
         self.compuMethodRef=None
      
class RecordDataType(DataType):
   @property
   def tag(self): return 'RECORD-TYPE'      
   def __init__(self,name,_elements):
      super().__init__(name)
      self.elements = []
      for elem in _elements:
         self.elements.append(RecordTypeElement(elem['name'],elem['typeRef']))
   def asdict(self):         
      data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
      if self.adminData is not None:
         data['adminData']=self.adminData.asdict()      
      for elem in self.elements:
         data['elements'].append(elem.asdict())
      return data

class ArrayDataType(DataType):
   @property
   def tag(self): return 'ARRAY-TYPE'
   
   def __init__(self,name,typeRef,length):
      super().__init__(name)
      self.typeRef = typeRef
      self.length = length

class BooleanDataType(DataType):
   @property
   def tag(self): return 'BOOLEAN-TYPE'
   
   def __init__(self,name):
      super().__init__(name)


class StringDataType(DataType):
   @property
   def tag(self): return 'STRING-TYPE'
   
   def __init__(self,name,length,encoding):
      super().__init__(name)
      self.length=length
      self.encoding=encoding
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'encoding':self.encoding,'length':self.length}
      return data

      
class RealDataType(DataType):
   @property
   def tag(self): return 'REAL-TYPE'
   
   def __init__(self,name,minval,maxval,minvalType='CLOSED',maxvalType='CLOSED',hasNaN=False,encoding='single'):
      super().__init__(name)
      self.minval=minval
      self.maxval=maxval
      self.minvalType = minvalType
      self.maxvalType = maxvalType
      self.hasNaN=hasNaN
      self.encoding=encoding
      

class CompuMethodRational(Element):   
   def __init__(self,name,unitRef,elements):      
      super().__init__(name)
      self.unitRef = unitRef
      self.elements = []
      for elem in elements:
         self.elements.append(CompuRationalElement(**elem))
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
      for element in self.elements:
         data['elements'].append(element.asdict())
      return data

      
class CompuMethodConst(Element):
   def __init__(self,name,elements):
      super().__init__(name)
      self.elements = []
      for elem in elements:
         if isinstance(elem,str):
            index=len(self.elements)
            self.elements.append(CompuConstElement(minvalue=index,maxvalue=index,textvalue=elem))
         elif isinstance(elem,dict):
            self.elements.append(CompuConstElement(**elem))
         elif isinstance(elem,tuple):
            if len(elem==2):
               self.elements.append(CompuConstElement(minvalue=elem[0],maxvalue=elem[0],textvalue=elem[1]))
            elif len(elem==3):
               self.elements.append(CompuConstElement(*elem))
            else:
               raise ValueError('invalid length: %d'%len(elem))
         else:
            raise ValueError('type not supported:%s'%str(type(elem)))
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
      for element in self.elements:
         data['elements'].append(element.asdict())
      return data

   
   def getValueTable(self):
      retval = []
      i = 0
      for elem in self.elements:
         if (elem.minvalue == elem.maxvalue) and elem.minvalue==i:
            retval.append(elem.textvalue)
         else:
            return None
         i+=1      
      return retval if len(retval)>0 else None



   
   

class DataTypeSemanticsPackage(object):
   def __init__(self):      
      self.elements=[]      
   def loadFromXML(self,root,version=3):
      parser = DataTypeSemanticsParser(self,version)
      parser.parse(root)
   
   def addCompuMethod(self,method):
      if isinstance(method,(CompuMethodConst,CompuMethodRational)):
         self.elements.append(method)
      else:
         raise ValueError('invalid type detected')
   
   def findCompuMethod(self,name):
      for elem in self.elements:
         if name==elem.name:
            return elem
      return None

class DataTypeUnitsPackage(object):
   def __init__(self):
      self.elements=[]
   
   def loadFromXML(self,root,version=3):
      parser = DataTypeUnitsParser(self,version)
      parser.parse(root)
      
   def addUnit(self,name,displayName):
      self.elements.append(DataTypeUnitElement(name,displayName))

   