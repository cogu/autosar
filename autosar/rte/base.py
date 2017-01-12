import autosar.datatype

class RteTypeManager:
   
   def __init__(self):
      self.typeMap = {}
   
   def processType(self, ws, dataType):
      if dataType.ref not in self.typeMap:         
         if isinstance(dataType, autosar.datatype.RecordDataType):
            for elem in dataType.elements:
               childType = ws.find(elem.typeRef, role='DataType')
               if childType is None:
                  raise ValueError('invalid reference: ' + elem.typeRef)
               self.processType(ws, childType)
            self.typeMap[dataType.ref]=dataType
         elif isinstance(dataType, autosar.datatype.ArrayDataType):
               childType = ws.find(dataType.typeRef, role='DataType')
               if childType is None:
                  raise ValueError('invalid reference: ' + elem.typeRef)
               self.processType(ws, childType)
               self.typeMap[dataType.ref]=dataType
         else:
            self.typeMap[dataType.ref]=dataType
   
   def getTypes(self, ws):
      basicTypes=set()
      complexTypes=set()
      modeTypes=set()
      
      for dataType in self.typeMap.values():
         if isinstance(dataType, autosar.datatype.RecordDataType) or isinstance(dataType, autosar.datatype.ArrayDataType):
            complexTypes.add(dataType.ref)
         elif isinstance(dataType, autosar.portinterface.ModeDeclarationGroup):
            modeTypes.add(dataType.ref)
         else:
            basicTypes.add(dataType.ref)
      return list(basicTypes),list(complexTypes),list(modeTypes)

         
         