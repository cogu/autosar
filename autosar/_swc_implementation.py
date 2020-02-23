from autosar.element import Element

class SwcImplementation(Element):
    """ Swc implementation """
    def __init__(self,name, behaviorRef, parent=None):
        super().__init__(name, parent)
        self.behaviorRef = behaviorRef
        self.codeDescriptors = None
        self.programmingLanguage = None
        self.resourceConsumption = None
        self.swVersion = None
        self.useCodeGenerator = None
        self.vendorId = None

class SwcImplementationCodeDescriptor(Element):
    """ Swc implementation code """
    def __init__(self,name, parent=None):
        super().__init__(name, parent)
        # Autosar 4
        self.artifactDescriptors = None

        # Autosar 3
        self.type = None

class EngineeringObject(object):
    """ EngineeringObject """
    def __init__(self, parent=None):
        self.parent = parent
        self.shortLabel = None
        self.category = None
        self.revisionLabels = None
        self.domain = None

class ResourceConsumption(Element):
    """ Swc implementation ResourceConsumption """
    def __init__(self,name, parent=None):
        super().__init__(name, parent)
        self.memorySections = None

class MemorySection(Element):
    """ Swc implementation MemorySection """
    def __init__(self,name, parent=None):
        super().__init__(name, parent)
        self.aligment = None
        self.memClassSymbol = None
        self.options = None
        self.size = None
        self.swAddrmethodRef = None
        self.symbol = None
