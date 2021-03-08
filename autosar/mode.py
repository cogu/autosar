from autosar.element import (Element, DataElement)
import collections
import autosar.base


class ModeGroup(Element):
    """
    Implements <MODE-GROUP> (AUTOSAR4)
    Implements <MODE-DECLARATION-GROUP-PROTOTYPE> (AUTOSAR3)

    A ModeGroup inside a ModeSwitchInterface is what a DataElement is to a SenderReceiverInterface.
    """
    def __init__(self, name, typeRef, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.typeRef=typeRef

    def tag(self,version=None):
        if version>=4.0:
            return "MODE-GROUP"
        else:
            return "MODE-DECLARATION-GROUP-PROTOTYPE"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.adminData == other.adminData and self.typeRef == other.typeRef: return True
        return False

    def __ne__(self, other):
        return not (self == other)

class ModeDeclarationGroup(Element):
    """
    Implements <MODE-DECLARATION-GROUP> (AUTOSAR 4)

    Objects created from this class is expected to be placed inside a package with the role name "ModeDclrGroup".

    Attributes:
    modeDeclarations: A list of ModeDeclaration objects
    initialModeRef: Initial mode value

    """
    def tag(self, version=None): return "MODE-DECLARATION-GROUP"

    def __init__(self, name, initialModeRef=None, modeDeclarations=None, category=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData, category)
        self.initialModeRef = initialModeRef
        if modeDeclarations is None:
            self.modeDeclarations = []
        else:
            self.modeDeclarations = list(modeDeclarations)
        self.category=category

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
    """
    Implements <MODE-DECLARATION> (AUTOSAR4)
    """
    def tag(self,version=None): return "MODE-DECLARATION"

    def __init__(self, name, value = None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.value = int(value) if value is not None else None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name:
                if self.value is None and other.value is None:
                    return True
                elif (self.value is not None) and (other.value is not None):
                    if self.value == other.value:
                        return True
        return False

    def __ne__(self, other): return not (self == other)