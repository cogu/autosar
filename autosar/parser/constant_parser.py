from autosar.element import Element
from autosar.constant import *
from autosar.base import hasAdminData,parseAdminDataNode

class ConstantPackageParser(object):
   """
   Constant package parser   
   """
   def __init__(self,pkg,version=3.0):
      if version == 3.0:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)      
                  
   def parseConstantSpecification(self,xmlRoot,rootProject=None,parent=None):
      assert(xmlRoot.tag == 'CONSTANT-SPECIFICATION')
      xmlName = xmlRoot.find('SHORT-NAME')
      if xmlName is not None:
         name = xmlName.text         
         xmlValue = xmlRoot.find('./VALUE/*')         
         if xmlValue is not None:
            constantValue = self.parseConstantValue(xmlValue)
         else:
            constantValue = None
         constant = Constant(name,constantValue)
         if hasAdminData(xmlRoot):
            constant.adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
         return constant
      return None
               
   def parseConstantValue(self,xmlValue):
      constantValue = None
      xmlName = xmlValue.find('SHORT-NAME')
      if xmlName is not None:
         name=xmlName.text
         if xmlValue.tag == 'INTEGER-LITERAL':
            typeRef = xmlValue.find('./TYPE-TREF').text
            innerValue = xmlValue.find('./VALUE').text
            constantValue = IntegerValue(name,typeRef,innerValue)
         elif xmlValue.tag=='STRING-LITERAL':
            typeRef = xmlValue.find('./TYPE-TREF').text
            innerValue = xmlValue.find('./VALUE').text
            constantValue = StringValue(name,typeRef,innerValue)
         elif xmlValue.tag=='BOOLEAN-LITERAL':
            typeRef = xmlValue.find('./TYPE-TREF').text
            innerValue = xmlValue.find('./VALUE').text
            constantValue = BooleanValue(name,typeRef,innerValue)
         elif xmlValue.tag == 'RECORD-SPECIFICATION' or xmlValue.tag == 'ARRAY-SPECIFICATION':
            typeRef = xmlValue.find('./TYPE-TREF').text
            if xmlValue.tag == 'RECORD-SPECIFICATION':
               constantValue=RecordValue(name,typeRef)                        
            else:
               constantValue=ArrayValue(name,typeRef)
            for innerElem in xmlValue.findall('./ELEMENTS/*'):               
               innerConstant = self.parseConstantValue(innerElem)
               if innerConstant is not None:
                  constantValue.elements.append(innerConstant)
                  innerConstant.parent=constantValue
      return constantValue
