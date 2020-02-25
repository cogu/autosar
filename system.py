from autosar.element import Element

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
    def __init__(self,dataElemInstanceRef,signalGroupRef,typeMapping):
        self.dataElemInstanceRef=dataElemInstanceRef
        self.signalGroupRef=signalGroupRef
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
