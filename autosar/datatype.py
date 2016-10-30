from autosar.package import Package
from autosar.element import Element
import math
import json
import copy

class ConstElement(object):
   def __init__(self,parent=None):
      self.parent=parent
   
   def asdict(self):
      data={'type': self.__class__.__name__}
      data.update(self.__dict__)
      return data
   def find(self,ref):
      if ref.startswith('/'):
         return self.root().find(ref)
      return None
   def rootWS(self):
      if self.parent is None: return None
      return self.parent.rootWS()
   


class RecordTypeElement(ConstElement):
   def __init__(self,name,typeRef,parent=None):
      super().__init__(parent)
      self.name=name
      self.typeRef=typeRef
   def __eq__(self,other):
      if self is other: return True
      if type(self) == type(other):
         if self.name == other.name:
            lhs = None if self.typeRef is None else self.find(self.typeRef)
            rhs = None if other.typeRef is None else other.find(other.typeRef)
            if lhs != rhs:
               print(self.name,self.typeRef)
            return lhs==rhs
      return False

class CompuConstElement(ConstElement):
   def __init__(self,minvalue,maxvalue,textvalue):
      self.minval=minvalue
      self.maxval=maxvalue
      self.textval=textvalue
   def __eq__(self,other):
      if self is other: return True
      if type(self) is type(other):
         return (self.minval == other.minval) and (self.maxval == other.maxval) and (self.textval == self.textval)      
      return False
      

class CompuRationalElement(ConstElement):
   def __init__(self,offset,numerator,denominator):
      self.offset=offset
      self.numerator=numerator
      self.denominator=denominator
   def __eq__(self,other):
      if self is other: return True
      if type(self) is type(other):
         return (self.offset == other.offset) and (self.numerator == other.numerator) and (self.denominator == self.denominator)      
      return False      

class DataTypeUnitElement(Element):
   def __init__(self,name,displayName):
      super().__init__(name)
      self.displayName=displayName
   def __eq__(self,other):
      if self is other: return True
      if type(self) is type(other):
         return (self.name==other.name) and (self.displayName == other.displayName)
      return False       

class DataType(Element):
   def __init__(self,name):
      super().__init__(name)
   
    


class IntegerDataType(DataType):
   
   def tag(self,version=None): return 'INTEGER-TYPE'
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
   def __eq__(self,other):
      if self is other: return True
      if type(other) is type(self):
         if (self.name==other.name) and (self.minval == other.minval) and (self.maxval==other.maxval):
            if (self.compuMethodRef is not None) and (other.compuMethodRef is not None):
               return self.findWS().find(self.compuMethodRef) == other.findWS().find(other.compuMethodRef)
            elif (self.compuMethodRef is None) and (other.compuMethodRef is None):
               return True
   
   def __deepcopy__(self,memo):
      obj=type(self)(self.name,self.minval,self.maxval,self.compuMethodRef)
      if self.adminData is not None: obj.adminData=copy.deepcopy(self.adminData,memo)
      return obj
            
class RecordDataType(DataType):
   
   def tag(self,version=None): return 'RECORD-TYPE'      
   def __init__(self,name,elements=None):
      super().__init__(name)
      self.elements = []
      if elements is not None:
         for elem in elements:
            self.elements.append(RecordTypeElement(elem['name'],elem['typeRef'],self))
   def asdict(self):         
      data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
      if self.adminData is not None:
         data['adminData']=self.adminData.asdict()      
      for elem in self.elements:
         data['elements'].append(elem.asdict())
      return data
   def __eq__(self, other):
      if self is other: return True
      if (self.name == other.name) and (len(self.elements)==len(other.elements)):
         for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]: return False
         return True
      return False

   def __deepcopy__(self,memo):
      obj=type(self)(self.name)      
      if self.adminData is not None: obj.adminData=copy.deepcopy(self.adminData,memo)
      for elem in self.elements:
         obj.elements.append(RecordTypeElement(elem.name,elem.typeRef,self))
      return obj
      
   
   

class ArrayDataType(DataType):
   
   def tag(self,version=None): return 'ARRAY-TYPE'
   
   def __init__(self,name,typeRef,length):
      super().__init__(name)
      self.typeRef = typeRef
      self.length = length

class BooleanDataType(DataType):
   
   def tag(self,version=None): return 'BOOLEAN-TYPE'
   
   def __init__(self,name):
      super().__init__(name)


class StringDataType(DataType):
   def tag(self,version=None): return 'STRING-TYPE'
   
   def __init__(self,name,length,encoding):
      super().__init__(name)
      self.length=length
      self.encoding=encoding
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'encoding':self.encoding,'length':self.length}
      return data
   def __eq__(self,other):
      if self is other: return False
      if type(self) == type(other):
         if (self.name==other.name) and (self.length == other.length) and (self.encoding == other.encoding):
            return True
      return False
   
   def __deepcopy__(self,memo):
      obj=type(self)(self.name,self.length,self.encoding)
      return obj

      
class RealDataType(DataType):
   def tag(self,version=None): return 'REAL-TYPE'
   
   def __init__(self,name,minval,maxval,minvalType='CLOSED',maxvalType='CLOSED',hasNaN=False,encoding='single'):
      super().__init__(name)
      self.minval=minval
      self.maxval=maxval
      self.minvalType = minvalType
      self.maxvalType = maxvalType
      self.hasNaN=hasNaN
      self.encoding=encoding
      

class CompuMethodRational(Element):
   def tag(self,version=None): return 'COMPU-INTERNAL-TO-PHYS'
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
   
   def find(self,ref):
      if ref.startswith('/'):
         root=self.rootWS()
         return root.find(ref)
      return None
   
   def __eq__(self,other):
      if self is other: return True
      if self.name == other.name:
         lhs = None if self.unitRef is None else self.find(self.unitRef)
         rhs = None if other.unitRef is None else other.find(other.unitRef)      
         if lhs == rhs:         
            if len(self.elements)!=len(other.elements): return False
            for i in range(len(self.elements)):
               if self.elements[i] != other.elements[i]: return False
            return True
      return False

      
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

   def __eq__(self,other):
      if self is other: return True
      if self.name == other.name:
         if len(self.elements)!=len(other.elements): return False
         for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]: return False
         return True
      return False
   