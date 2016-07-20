from autosar.base import parseXMLFile,splitref,parseTextNode,parseIntNode,hasAdminData,parseAdminDataNode
from autosar.element import Element
import json
import sys



class System(Element):
   def __init__(self,name,parent=None):
      super().__init__(name,parent)
      self.fibexElementRefs=[]
      self.mapping=None
      self.softwareComposition=None
   
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,
            }
      if len(self.fibexElementRefs)>0:
         data['fibexElementRefs']=self.fibexElementRefs[:]
      return data

class DataMapping:
   def __init__(self):
      self.swcToImpl=[]
      self.senderReceiverToSignal=[]
      self.senderReceiverToSignalGroup=[]

class Mapping:
   def __init__(self,name=None,parent=None):
      self.name=None
      self.data=DataMapping()

class SenderReceiverToSignalMapping:
   """
   <SENDER-RECEIVER-TO-SIGNAL-MAPPING>
   """
   def __init__(self,dataElemInstanceRef,signalRef):      
      self.dataElemInstanceRef=dataElemInstanceRef
      self.signalRef=signalRef

class SignalDataElementInstanceRef:
   """
   <DATA-ELEMENT-IREF>
   Note: Observe that there are multiple <DATA-ELEMENT-IREF> definitions in the AUTOSAR XSD (used for different purposes)
   """
   def __init__(self,dataElemRef):      
      self.dataElemRef = dataElemRef      #minOccurs=1, maxOccurs=1
      self.softwareCompositionRef=None    #minOccurs=0, maxOccurs=1
      self.componentPrototypeRef=[]       #minOccurs=0, maxOccurs=unbounded
      self.portPrototypeRef=None          #minOccurs=0, maxOccurs=1
   def asdict(self):
      data={'type': self.__class__.__name__,'dataElemRef':self.dataElemRef}
      return data         

class SenderReceiverToSignalGroupMapping:
   """
   <SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING>
   """
   def __init__(self,dataElemInstanceRef,signalRef,typeMapping):      
      self.dataElemInstanceRef=dataElemInstanceRef
      self.signalRef=signalRef
      self.typeMapping=typeMapping

class TypeMapping:
   def __init__(self):
      self.elements=[]


class ArrayElementMapping(TypeMapping):
   def __init__(self):
      super().__init__()

class RecordElementMapping(TypeMapping):
   def __init__(self):
      super().__init__()

class SenderRecRecordElementMapping:
   def __init__(self,recordElementRef,signalRef):
      self.recordElementRef=recordElementRef
      self.signalRef=signalRef

#########################################
class SystemParser(object):
   def __init__(self,pkg,version=3):
      if version == 3:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.pkg=pkg
   
   def parseSystem(self,xmlRoot,dummy,parent=None):
      """
      parses <SYSTEM>
      """
      assert(xmlRoot.tag=='SYSTEM')
      xmlName = xmlRoot.find('SHORT-NAME')
      if xmlName is not None:
         system=System(parseTextNode(xmlName),parent)
         for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='SHORT-NAME':
               pass
            elif xmlElem.tag=='ADMIN-DATA':
               system.adminData=parseAdminDataNode(xmlElem)
            elif xmlElem.tag=='FIBEX-ELEMENT-REFS':
               self.parseFibexElementRefs(xmlElem,system)
            elif xmlElem.tag=='MAPPING':
               self.parseSystemMapping(xmlElem,system)
            elif xmlElem.tag=='SOFTWARE-COMPOSITION':
               self.parseSoftwareComposition(xmlElem,system)
            else:
               raise NotImplementedError(xmlElem.tag)
         return system
      else:
         raise KeyError('expected to find <SHORT-NAME> inside <SYSTEM> tag')
   
   def parseFibexElementRefs(self,xmlRoot,system):
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag=='FIBEX-ELEMENT-REF':
            system.fibexElementRefs.append(parseTextNode(xmlElem))
         else:
            raise NotImplementedError(xmlElem.tag)
   
   def parseSystemMapping(self,xmlRoot,system):
      """parses <MAPPING>"""
      assert(xmlRoot.tag=='MAPPING')
      name=parseTextNode(xmlRoot.find('SHORT-NAME'))
      system.mapping = Mapping(name,system)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag=='SHORT-NAME':
            pass
         elif xmlElem.tag=='DATA-MAPPINGS':
            self.parseDataMapping(xmlElem,system.mapping.data)
         elif xmlElem.tag=='SW-IMPL-MAPPINGS':
            self.parseSwImplMapping(xmlElem,system.mapping)
         elif xmlElem.tag=='SW-MAPPINGS':
            self.parseSwMapping(xmlElem,system.mapping)
         else:
            raise NotImplementedError(xmlElem.tag)
   
   def parseDataMapping(self,xmlRoot,dataMapping):
      """parses <DATA-MAPPINGS>"""
      assert(xmlRoot.tag=='DATA-MAPPINGS')
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag=='SWC-TO-IMPL-MAPPING':
            pass
         elif xmlElem.tag=='SENDER-RECEIVER-TO-SIGNAL-MAPPING':
            dataMapping.senderReceiverToSignal.append(self.parseSenderReceiverToSignalMapping(xmlElem))
         elif xmlElem.tag=='SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING':
            dataMapping.senderReceiverToSignalGroup.append(self.parseSenderReceiverToSignalGroupMapping(xmlElem))
         else:
            raise NotImplementedError(xmlElem.tag)

   def parseSwImplMapping(self,xmlRoot,mapping):
      """parses <SW-IMPL-MAPPINGS>"""
      assert(xmlRoot.tag=='SW-IMPL-MAPPINGS')
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag=='SWC-TO-IMPL-MAPPING':
            pass
         else:
            raise NotImplementedError(xmlElem.tag)

   def parseSwMapping(self,xmlRoot,mapping):
      """parses <SW-MAPPINGS>"""
      assert(xmlRoot.tag=='SW-MAPPINGS')
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag=='SWC-TO-ECU-MAPPING':
            pass
         else:
            raise NotImplementedError(xmlElem.tag)
   
   def parseSoftwareComposition(self,xmlRoot,system):
      """parses <SOFTWARE-COMPOSITION>"""
      assert(xmlRoot.tag=='SOFTWARE-COMPOSITION')
      name=parseTextNode(xmlRoot.find('SHORT-NAME'))
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag=='SHORT-NAME':
            pass
         elif xmlElem.tag=='SOFTWARE-COMPOSITION-TREF':
            pass
         else:
            raise NotImplementedError(xmlElem.tag)

   def parseSenderReceiverToSignalMapping(self,xmlRoot):
      """parses <'SENDER-RECEIVER-TO-SIGNAL-MAPPING'>"""
      assert(xmlRoot.tag=='SENDER-RECEIVER-TO-SIGNAL-MAPPING')
      dataElemIRef=None
      signalRef=None     
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag=='DATA-ELEMENT-IREF':
            dataElemIRef=self.parseDataElemInstanceRef(xmlElem)
         elif xmlElem.tag=='SIGNAL-REF':
            signalRef=parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (dataElemIRef is not None) and (signalRef is not None):
         return SenderReceiverToSignalMapping(dataElemIRef,signalRef)
      else:
         raise Exception("failed to parse SENDER-RECEIVER-TO-SIGNAL-MAPPING")

   def parseSenderReceiverToSignalGroupMapping(self,xmlRoot):      
      """parses <'SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING'>"""
      assert(xmlRoot.tag=='SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING')
      dataElemIRef=None
      signalGroupRef=None
      typeMapping=None
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'DATA-ELEMENT-IREF': #minOccurs=0, maxOccurs=1
            dataElemIRef=self.parseDataElemInstanceRef(xmlElem)
         elif xmlElem.tag == 'SIGNAL-GROUP-REF': #minOccurs=0, maxOccurs=
            signalGroupRef=parseTextNode(xmlElem)
         elif xmlElem.tag == 'TYPE-MAPPING': #minOccurs=0, maxOccurs=1
            for xmlChild in xmlElem.findall('./*'):
               if xmlChild.tag=='SENDER-REC-ARRAY-TYPE-MAPPING':
                  typeMapping = ArrayElementMapping()
                  for xmlItem in xmlChild.findall('./ARRAY-ELEMENT-MAPPINGS/SENDER-REC-ARRAY-TYPE-MAPPING'):
                     print("SENDER-REC-ARRAY-TYPE-MAPPING not implemented")
               elif xmlChild.tag=='SENDER-REC-RECORD-TYPE-MAPPING':
                  typeMapping=RecordElementMapping()
                  for xmlItem in xmlChild.findall('./RECORD-ELEMENT-MAPPINGS/SENDER-REC-RECORD-ELEMENT-MAPPING'):
                     typeMapping.elements.append(self.parseSenderRecRecordElementMapping(xmlItem))
               else:
                  raise NotImplementedError(xmlChild.tag)                              
         else:
            raise NotImplementedError(xmlElem.tag)
      return SenderReceiverToSignalGroupMapping(dataElemIRef,signalGroupRef,typeMapping)

   def parseDataElemInstanceRef(self,xmlRoot):
      dataElemRef=parseTextNode(xmlRoot.find('DATA-ELEMENT-REF'))
      assert(dataElemRef is not None)
      dataElemIRef=SignalDataElementInstanceRef(dataElemRef)
      for xmlChild in xmlRoot.findall('./*'):
         if xmlChild.tag=='DATA-ELEMENT-REF':
            pass
         elif xmlChild.tag=='SOFTWARE-COMPOSITION-REF':
            dataElemIRef.softwareCompositionRef=parseTextNode(xmlChild)
         elif xmlChild.tag=='COMPONENT-PROTOTYPE-REF':
            dataElemIRef.componentPrototypeRef.append(parseTextNode(xmlChild))
         elif xmlChild.tag=='PORT-PROTOTYPE-REF':
            dataElemIRef.portPrototypeRef=parseTextNode(xmlChild)
         else:
            raise NotImplementedError(xmlChild.tag)
      return dataElemIRef
   
   def parseSenderRecRecordElementMapping(self,xmlRoot):
      """parses <'SENDER-REC-RECORD-ELEMENT-MAPPING'>"""      
      assert(xmlRoot.tag=='SENDER-REC-RECORD-ELEMENT-MAPPING')
      recordElementRef=None
      signalRef=None
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag=='RECORD-ELEMENT-REF': #minOccurs="0" maxOccurs="1"
            recordElementRef=parseTextNode(xmlElem)
         elif xmlElem.tag=='SIGNAL-REF': #minOccurs="0" maxOccurs="1"
            signalRef=parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      return SenderRecRecordElementMapping(recordElementRef,signalRef)

   def parseSenderRecArrayElementMapping(self,xmlRoot):
      """parses <'SENDER-REC-RECORD-ELEMENT-MAPPING'>"""      
      assert(xmlRoot.tag=='SENDER-REC-RECORD-ELEMENT-MAPPING')
      raise NotImplementedError(xmlRoot.tag)
