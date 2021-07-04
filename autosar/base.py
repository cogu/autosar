import xml.etree.ElementTree as ElementTree
import re

pVersion = re.compile(r"(\d+)\.(\d+)\.(\d+)")

class AdminData:
    def __init__(self):
        self.specialDataGroups = []
    def asdict(self):
        retval={'type': self.__class__.__name__, 'specialDataGroups':[]}
        for elem in self.specialDataGroups:
            retval['specialDataGroups'].append(elem.asdict())
        return retval

    def __eq__(self, other):
        if isinstance(other, self.__class__) and len(self.specialDataGroups) == len(other.specialDataGroups):
            for i,elem in enumerate(self.specialDataGroups):
                if elem != other.specialDataGroups[i]:
                    return False
            return True
        return False

    def __ne__(self, other): return not (self == other)

class SpecialDataGroup(object):
    def __init__(self,SDG_GID,SD=None,SD_GID=None):
        self.SDG_GID=SDG_GID
        self.SD = []
        if SD is not None or SD_GID is not None:
            self.SD.append(SpecialData(SD, SD_GID))

    # def asdict(self):
    #    data = {'type': self.__class__.__name__}
    #    if self.SDG_GID is not None: data['SDG_GID']=self.SDG_GID
    #    if self.SD is not None: data['SD']=self.SD
    #    if self.SD_GID is not None: data['SD_GID']=self.SD_GID
    #    return data

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.SDG_GID == other.SDG_GID:
                for i,SD in enumerate(self.SD):
                    other_SD = other.SD[i]
                    if SD.TEXT != other_SD.TEXT or SD.GID != other_SD.GID:
                        return False
                return True
        return False

    def __ne__(self, other): return not (self == other)

class SpecialData:
    def __init__(self, TEXT, GID):
        self.TEXT = TEXT
        self.GID = GID

def removeNamespace(doc, namespace):
    """Removes XML namespace in place."""
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.iter():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]

def parseXMLFile(filename,namespace=None):
    arxml_tree = ElementTree.ElementTree()
    arxml_tree.parse(filename)
    arxml_root = arxml_tree.getroot()
    if namespace is not None:
        removeNamespace(arxml_root,namespace)
    return arxml_root

def getXMLNamespace(element):
    m = re.match(r'\{(.*)\}', element.tag)
    return m.group(1) if m else None

def splitRef(ref):
    """splits an autosar url string into an array"""
    if isinstance(ref,str):
        if ref[0]=='/': return ref[1:].split('/')
        else: return ref.split('/')
    return None

def hasAdminData(xmlRoot):
    return True if xmlRoot.find('ADMIN-DATA') is not None else False

def parseAdminDataNode(xmlRoot):
    if xmlRoot is None: return None
    assert(xmlRoot.tag=='ADMIN-DATA')
    adminData=AdminData()
    xmlSDGS = xmlRoot.find('./SDGS')
    if xmlSDGS is not None:
        for xmlElem in xmlSDGS.findall('./SDG'):
            GID=xmlElem.attrib['GID']
            SD=None
            SD_GID=None
            xmlSD = xmlElem.find('SD')
            if xmlSD is not None:
                SD=xmlSD.text
                try:
                    SD_GID=xmlSD.attrib['GID']
                except KeyError: pass
            adminData.specialDataGroups.append(SpecialDataGroup(GID,SD,SD_GID))
    return adminData

def parseTextNode(xmlElem):
    return None if xmlElem is None else xmlElem.text
def parseIntNode(xmlElem):
    return None if xmlElem is None else int(xmlElem.text)
def parseFloatNode(xmlElem):
    return None if xmlElem is None else float(xmlElem.text)
def parseBooleanNode(xmlElem):
    return None if xmlElem is None else parseBoolean(xmlElem.text)

def parseBoolean(value):
    if value is None:
        return None
    if isinstance(value,str):
        if value == 'true': return True
        elif value =='false': return False
    raise ValueError(value)

def indexByName(lst,name):
    assert(isinstance(lst,list))
    assert(isinstance(name,str))
    for i,item in enumerate(lst):
        if item.name == name: return i
    raise ValueError('%s not in list'%name)

def createAdminData(data):
    adminData = AdminData()
    SDG_GID = data.get('SDG_GID',None)
    if 'SDG' in data:
        group = SpecialDataGroup(SDG_GID)
        for item in data['SDG']:
            SD_GID = item.get('SD_GID',None)
            SD = item.get('SD',None)
            group.SD.append(SpecialData(SD, SD_GID))
        adminData.specialDataGroups.append(group)
    else:
        SD_GID = data.get('SD_GID',None)
        SD = data.get('SD',None)
        adminData.specialDataGroups.append(SpecialDataGroup(SDG_GID,SD,SD_GID))
    return adminData

def parseAutosarVersionAndSchema(xmlRoot):
    """
    Parses AUTOSAR version from the schemaLocation attribute in the root AUTOSAR tag

    For AUTOSAR versions 4.3 and below (e.g. "http://autosar.org/schema/r4.0 AUTOSAR_4-3-0.xsd")
    Returns a tuple with major, minor, patch, None, schemaFile. Types are (int, int, int, NoneType, str)

    For AUTOSAR versions 4.4 and above (e.g. "http://autosar.org/schema/r4.0 AUTOSAR_00044.xsd")
    Returns a tuple with major, minor, None, release, schemaFile
    This will now report (major,minor) as (4,0) since it will now extract from the "r4.0"-part of the attribute.
    """
    schemaLocation = None
    for key in xmlRoot.attrib.keys():
        if key.endswith('schemaLocation'):
            value = xmlRoot.attrib[key]
            #Retreive the schema file
            result = re.search(r'(^[ ]+\.xsd)', value)
            tmp = value.partition(' ')
            if len(tmp[2])>0:
                schemaFile = tmp[2]
            else:
                schemaFile = None
            #Is this AUTOSAR 3?
            result = re.search(r'(\d)\.(\d)\.(\d)', value)
            if result is not None:
                return (int(result.group(1)), int(result.group(2)), int(result.group(3)), None,  schemaFile)
            else:
                #Is this AUTOSAR 4.0 to 4.3?
                result = re.search(r'(\d)-(\d)-(\d).*\.xsd', value)
                if result is not None:
                    return (int(result.group(1)),int(result.group(2)),int(result.group(3)), None, schemaFile)
                else:
                    #Is this AUTOSAR 4.4 or above?
                    result = re.search(r'r(\d+)\.(\d+)\s+AUTOSAR_(\d+).xsd', value)
                    if result is not None:
                        return (int(result.group(1)),int(result.group(2)),None, int(result.group(3)), schemaFile)

    return (None, None, None, None, None)

def applyFilter(ref, filters):
    if filters is None:
        return True

    if ref[0] == '/': ref=ref[1:]
    tmp = ref.split('/')

    for f in filters:
        match = True
        for i,filter_elem in enumerate(f):
            if i >=len(tmp): return True
            ref_elem = tmp[i]
            if (filter_elem != '*') and (ref_elem != filter_elem):
                match = False
                break
        if match: return True
    return False


def prepareFilter(fstr):
    if fstr[0] == '/': fstr=fstr[1:]
    if fstr[-1] == '/': fstr+='*'
    return fstr.split('/')

def parseVersionString(versionString):
    """
    takes a string of the format <major>.<minor>.<patch> (e.g. "3.2.2") and returns a tuple with three integers (major, minor, patch)
    """
    result = pVersion.match(versionString)
    if result is None:
        raise ValueError("VersionString argument did not match the pattern '<major>.<minor>.<patch>'")
    else:
        return (int(result.group(1)),int(result.group(2)),int(result.group(3)))

def findUniqueNameInList(elementList, baseName):
    """
    Attempts to find a unique name in the list of objects based on baseName.
    This function can modify names in gived list.
    Returns a new name which is guaranteed to be unique
    """

    foundElem = None
    highestIndex = 0
    hasIndex = False
    p0 = re.compile(baseName+r'_(\d+)')
    for elem in elementList:
        result = p0.match(elem.name)
        if result is not None:
            hasIndex = True
            index = int(result.group(1))
            if index > highestIndex:
                highestIndex = index
        elif elem.name == baseName:
            foundElem = elem
    if foundElem is not None:
        foundElem.name = '_'.join([foundElem.name, '0'])
    if hasIndex or foundElem is not None:
        return '_'.join([baseName, str(highestIndex+1)])
    else:
        return baseName



class SwDataDefPropsConditional:
    def tag(self,version=None): return 'SW-DATA-DEF-PROPS-CONDITIONAL'
    def __init__(self, baseTypeRef = None, implementationTypeRef = None, swAddressMethodRef = None, swCalibrationAccess = None, swImplPolicy = None, swPointerTargetProps = None, compuMethodRef = None, dataConstraintRef = None, unitRef = None, parent = None):
        self.baseTypeRef = baseTypeRef
        self.swCalibrationAccess = swCalibrationAccess
        self.swAddressMethodRef = swAddressMethodRef
        self.compuMethodRef = compuMethodRef
        self.dataConstraintRef = dataConstraintRef
        self.implementationTypeRef = implementationTypeRef
        self.swPointerTargetProps = swPointerTargetProps
        self.unitRef = unitRef
        self.swImplPolicy = swImplPolicy
        self.parent = parent

    @property
    def swImplPolicy(self):
        return self._swImplPolicy

    @swImplPolicy.setter
    def swImplPolicy(self, value):
        if value is None:
            self._swImplPolicy=None
        else:
            ucvalue=str(value).upper()
            enum_values = ["CONST", "FIXED", "MEASUREMENT-POINT", "QUEUED", "STANDARD"]
            if ucvalue in enum_values:
                self._swImplPolicy = ucvalue
            else:
                raise ValueError('invalid swImplPolicy value: ' +  value)

    def hasAnyProp(self):
        """
        Returns True if any internal attribute is not None, else False.
        The check excludes the parent attribute.
        """
        retval = False
        attr_names = ['baseTypeRef',
                      'swCalibrationAccess',
                      'swAddressMethodRef',
                      'compuMethodRef',
                      'dataConstraintRef',
                      'implementationTypeRef',
                      'swPointerTargetProps',
                      'unitRef',
                      'swImplPolicy'
                      ]
        for name in attr_names:
            if getattr(self, name) is not None:
                retval = True
                break
        return retval

class SwPointerTargetProps:
    """
    (AUTOSAR 4)
    Implements <SW-POINTER-TARGET-PROPS>
    """
    def tag(self, version=None): return 'SW-POINTER-TARGET-PROPS'
    def __init__(self, targetCategory=None, variants = None):
        self.targetCategory = targetCategory
        if variants is None:
            self.variants = []
        else:
            if isinstance(variants, SwDataDefPropsConditional):
                self.variants = [variants]
            else:
                self.variants = list(variants)

class SymbolProps:
    """
    (AUTOSAR 4)
    Implements <SYMBOL-PROPS>
    """
    def tag(self, version=None): return 'SYMBOL-PROPS'

    def __init__(self, name = None, symbol = None):
        self.name = name
        self.symbol = symbol


#Exceptions
class InvalidUnitRef(ValueError):
    pass

class InvalidPortInterfaceRef(ValueError):
    pass

class InvalidComponentTypeRef(ValueError):
    pass

class InvalidDataTypeRef(ValueError):
    pass

class InvalidDataElementRef(ValueError):
    pass

class InvalidPortRef(ValueError):
    pass

class InvalidInitValueRef(ValueError):
    pass

class InvalidDataConstraintRef(ValueError):
    pass

class InvalidCompuMethodRef(ValueError):
    pass

class DataConstraintError(ValueError):
    pass

class InvalidMappingRef(ValueError):
    pass

class InvalidModeGroupRef(ValueError):
    pass

class InvalidModeDeclarationGroupRef(ValueError):
    pass

class InvalidModeDeclarationRef(ValueError):
    pass

class InvalidEventSourceRef(ValueError):
    pass

class InvalidRunnableRef(ValueError):
    pass

class InvalidBehaviorRef(ValueError):
    pass

class InvalidSwAddrmethodRef(ValueError):
    pass
