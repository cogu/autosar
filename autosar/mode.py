from autosar.element import (Element, DataElement)
import collections
import autosar.base


class ModeGroup(Element):
    def __init__(self, name, typeRef, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.typeRef=typeRef

    def tag(self,version=None):
        if version>=4.0:
            return "MODE-GROUP"
        else:
            return "MODE-DECLARATION-GROUP-PROTOTYPE"

    def asdict(self):
        return {'type': self.__class__.__name__, 'name':self.name, 'typeRef':self.typeRef}

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.adminData == other.adminData and self.typeRef == other.typeRef: return True
        return False

    def __ne__(self, other):
        return not (self == other)

class ModeDeclarationGroup(Element):
    def tag(self, version=None): return "MODE-DECLARATION-GROUP"

    def __init__(self, name, initialModeRef=None, modeDeclarations=None, category=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
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
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name: return True
        return False

    def __ne__(self, other): return not (self == other)

    def tag(self,version=None): return "MODE-DECLARATION"
    