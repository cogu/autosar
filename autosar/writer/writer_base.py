import abc
import autosar.base
import xml.sax.saxutils
import json
import collections
from autosar.element import DataElement
from decimal import Decimal

class BaseWriter:
    def __init__(self, version=3.0, patch=None):
        self.version=version
        d = Decimal(float(version))
        self.major=int(d.quantize(1))
        self.minor=int(((d%1)*10).quantize(1))
        if patch is None:
            self.patch = 0
        else:
            self.patch = int(patch)

        if (self.version >= 3.0) and (self.version < 4.0):
            self.indentChar='\t'
        else:
            self.indentChar = '  '

    def indent(self,lines,indent):
        if isinstance(lines,list):
            return ['%s%s'%(self.indentChar*indent,x) for x in lines]
        elif isinstance(lines,str):
            return '%s%s'%(self.indentChar*indent,lines)
        else:
            raise NotImplementedError(type(lines))


    def beginPackage(self, name,indent=None):
        lines = []
        lines.append('<AR-PACKAGE>')
        lines.append(self.indentChar+'<SHORT-NAME>%s</SHORT-NAME>'%name)
        return lines

    def endPackage(self,indent=None):
        lines = []
        lines.append('</AR-PACKAGE>')
        return lines

    def toBoolean(self,value):
        if value: return 'true'
        return 'false'

    def writeAdminDataXML(self,elem):
        assert(isinstance(elem,autosar.base.AdminData))
        lines = []
        lines.append('<ADMIN-DATA>')
        if len(elem.specialDataGroups)>0:
            lines.append(self.indent('<SDGS>',1))
            for sdg in elem.specialDataGroups:
                if sdg.SDG_GID is not None:
                    lines.append(self.indent('<SDG GID="%s">'%sdg.SDG_GID,2))
                else:
                    lines.append(self.indent('<SDG>',2))
                for sd in sdg.SD:
                    if (sd.TEXT is not None) and (sd.GID is not None):
                        lines.append(self.indent('<SD GID="%s">%s</SD>'%(sd.GID, sd.TEXT),3))
                    elif (sd.TEXT is None) and (sd.GID is not None):
                        lines.append(self.indent('<SD GID="%s"></SD>'%(sd.GID),3))
                    elif (sd.TEXT is not None) and (sd.GID is None):
                        lines.append(self.indent('<SD>%s</SD>'%(sd.TEXT),3))
                lines.append(self.indent('</SDG>',2))
            lines.append(self.indent('</SDGS>',1))
        else:
            lines.append('<SDGS/>')
        lines.append('</ADMIN-DATA>')
        return lines

    def writeDescXML(self,elem):
        if hasattr(elem,'desc'):
            if hasattr(elem,'descAttr'):
                descAttr=elem.descAttr
            else:
                descAttr='FOR-ALL'
            lines = []
            lines.append('<DESC>')
            if elem.desc is None or len(elem.desc)==0:
                lines.append(self.indent('<L-2 L="%s" />'%(descAttr),1))
            else:
                lines.append(self.indent('<L-2 L="%s">%s</L-2>'%(descAttr,xml.sax.saxutils.escape(elem.desc)),1))
            lines.append('</DESC>')
            return lines
        return None

    def writeDescCode(self, elem):
        if hasattr(elem,'desc'):
            if hasattr(elem,'descAttr') and (elem.descAttr != "FOR-ALL"):
                descAttr=elem.descAttr
            else:
                descAttr=None
            return elem.desc,descAttr
        return None,None

    def writeListCode(self, varname, data):
        """
        writes data as as an array with varname
        """
        lines=['','%s = ['%varname] #add newline at beginning to make reading easier
        indent=' '*(len(varname)+6)
        for i,elem in enumerate(data):
            if i+1==len(data):
                lines.append('%s%s'%(indent,str(elem)))
            else:
                lines.append('%s%s,'%(indent,str(elem)))
        indent=' '*(len(varname)+3)
        lines.append('%s]'%indent)
        return lines

    def writeDictCode(self, varname, data):
        """
        same as writeListCode but replaces surrounding [] with {}
        """
        lines=['','%s = {'%varname] #add newline at beginning to make reading easier
        indent=' '*(len(varname)+6)
        for i,elem in enumerate(data):
            if i+1==len(data):
                lines.append('%s%s'%(indent,str(elem)))
            else:
                lines.append('%s%s,'%(indent,str(elem)))
        indent=' '*(len(varname)+3)
        lines.append('%s}'%indent)
        return lines

    def writeAdminDataCode(self, adminData, localvars):
        """
        turns an autosar.base.AdminData object into a create call from ws
        """
        items=[]
        for sdg in adminData.specialDataGroups:
            data=collections.OrderedDict()
            if sdg.SDG_GID is not None: data['SDG_GID']=sdg.SDG_GID
            if len(sdg.SD) == 1:
                if sdg.SD[0].GID is not None: data['SD_GID']=sdg.SD[0].GID
                if sdg.SD[0].TEXT is not None: data['SD']=sdg.SD[0].TEXT
            items.append(data)
        if len(items)==0:
            raise ValueError("adminData doesn't seem to contain any SpecialDataGroups")
        elif len(items)==1:
            return json.dumps(items[0])
        else:
            return json.dumps(items)

    def writeSwDataDefPropsVariantsXML(self, ws, variants):
        lines = []
        lines.append(self.indent("<SW-DATA-DEF-PROPS-VARIANTS>", 0))
        for variant in variants:
            if isinstance(variant, autosar.base.SwDataDefPropsConditional):
                lines.extend(self.indent(self.writeSwDataDefPropsConditionalXML(ws, variant), 1))
            else:
                raise NotImplementedError(str(type(variant)))
        lines.append(self.indent("</SW-DATA-DEF-PROPS-VARIANTS>", 0))
        return lines

    def writeSwDataDefPropsConditionalXML(self, ws, elem):
        assert(isinstance(elem, autosar.base.SwDataDefPropsConditional))

        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        if elem.baseTypeRef is not None:
            baseType=ws.find(elem.baseTypeRef)
            if baseType is None:
                raise ValueError('invalid reference: '+elem.baseTypeRef)
            lines.append(self.indent('<BASE-TYPE-REF DEST="%s">%s</BASE-TYPE-REF>'%(baseType.tag(self.version), baseType.ref),1))
        if elem.swAddressMethodRef is not None:
            swAddressMethod = ws.find(elem.swAddressMethodRef)
            if swAddressMethod is None:
                raise ValueError('invalid SW-ADDRESS-METHOD reference: '+ elem.swAddressMethodRef)
            lines.append(self.indent('<SW-ADDR-METHOD-REF DEST="%s">%s</SW-ADDR-METHOD-REF>'%(swAddressMethod.tag(self.version), swAddressMethod.ref),1))
        if elem.swCalibrationAccess is not None:
            lines.append(self.indent('<SW-CALIBRATION-ACCESS>%s</SW-CALIBRATION-ACCESS>'%(elem.swCalibrationAccess),1))
        if elem.compuMethodRef is not None:
            lines.append(self.indent('<COMPU-METHOD-REF DEST="COMPU-METHOD">%s</COMPU-METHOD-REF>'%(elem.compuMethodRef),1))
        if elem.dataConstraintRef is not None:
            dataConstraint = ws.find(elem.dataConstraintRef)
            if dataConstraint is None:
                raise ValueError('invalid reference: '+ elem.dataConstraintRef)
            lines.append(self.indent('<DATA-CONSTR-REF DEST="%s">%s</DATA-CONSTR-REF>'%(dataConstraint.tag(self.version), dataConstraint.ref),1))
        if elem.swImplPolicy is not None:
            lines.append(self.indent('<SW-IMPL-POLICY>%s</SW-IMPL-POLICY>'%(elem.swImplPolicy),1))
        if elem.implementationTypeRef is not None:
            implementationType=ws.find(elem.implementationTypeRef)
            if implementationType is None:
                raise ValueError('invalid reference: '+elem.implementationTypeRef)
            lines.append(self.indent('<IMPLEMENTATION-DATA-TYPE-REF DEST="%s">%s</IMPLEMENTATION-DATA-TYPE-REF>'%(implementationType.tag(self.version), implementationType.ref),1))
        if elem.swPointerTargetProps is not None:
            lines.extend(self.indent(self.writeSwPointerTargetPropsXML(ws, elem.swPointerTargetProps),1))
        if elem.unitRef is not None:
            unit=ws.find(elem.unitRef)
            if unit is None:
                raise ValueError('invalid reference: '+elem.unitRef)
            lines.append(self.indent('<UNIT-REF DEST="UNIT">%s</UNIT-REF>'%(unit.ref),1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines


    def _createTypeRef(self, typeRef, localvars):
        """
        returns a represenation of a typeRef string
        if role 'DataType' is setup in the workspace it will only return the name of the reference,
        otherwise it returns the full reference
        """
        return self._createRef(componentRef, 'DataType', localvars)

    def _createComponentRef(self, componentRef, localvars):
        """
        returns a represenation of a componentRef string
        if role 'ComponentType' is setup in the workspace it will only return the name of the reference,
        otherwise it returns the full reference
        """
        return self._createRef(componentRef, 'ComponentType', localvars)

    def _createRef(self, ref, role, localvars):
        ws=localvars['ws']
        assert(ws is not None)
        element = ws.find(ref)
        if element is None:
            raise ValueError('invalid reference: '+ref)
        if ws.roles[role] is not None:
            return element.name #use name only
        else:
            return element.ref #use full reference

    def writeValueSpecificationXML(self, value):
        lines=[]
        lines.append('<%s>'%value.tag(self.version))
        if isinstance(value, autosar.constant.TextValue):
            lines.extend(self.indent(self._writeSimpleValueSpecificationXML(value),1))
        elif isinstance(value, autosar.constant.NumericalValue):
            lines.extend(self.indent(self._writeSimpleValueSpecificationXML(value),1))
        elif isinstance(value, autosar.constant.RecordValue):
            lines.extend(self.indent(self._writeRecordValueSpecificationXML(value),1))
        elif isinstance(value, autosar.constant.ArrayValue):
            lines.extend(self.indent(self._writeArrayValueSpecificationXML(value),1))
        else:
            raise NotImplementedError(str(type(value)))
        lines.append('</%s>'%value.tag(self.version))
        return lines

    def _writeSimpleValueSpecificationXML(self, value):
        lines=[]
        if value.name is not None:
            lines.append('<SHORT-LABEL>%s</SHORT-LABEL>'%(value.name))
        lines.append('<VALUE>%s</VALUE>'%(value.value))
        return lines

    def _writeRecordValueSpecificationXML(self, value):
        lines=[]
        if value.name is not None:
            lines.append('<SHORT-LABEL>%s</SHORT-LABEL>'%(value.name))
        lines.append('<FIELDS>')
        for elem in value.elements:
            lines.extend(self.indent(self.writeValueSpecificationXML(elem),1))
        lines.append('</FIELDS>')
        return lines

    def _writeArrayValueSpecificationXML(self, value):
        lines=[]
        if value.name is not None:
            lines.append('<SHORT-LABEL>%s</SHORT-LABEL>'%(value.name))
        lines.append('<ELEMENTS>')
        for elem in value.elements:
            lines.extend(self.indent(self.writeValueSpecificationXML(elem),1))
        lines.append('</ELEMENTS>')
        return lines

    def writeDataElementXML(self, elem):
        assert(isinstance(elem,DataElement))
        lines=[]
        ws = elem.rootWS()
        lines.append('<%s>'%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        if self.version >= 4.0:
            lines.append(self.indent('<SW-DATA-DEF-PROPS>',1))
            variant = autosar.base.SwDataDefPropsConditional(swAddressMethodRef = elem.swAddressMethodRef, swCalibrationAccess = elem.swCalibrationAccess, swImplPolicy = elem.swImplPolicy)
            variant.dataConstraintRef = elem.dataConstraintRef
            lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, [variant]),2))
            lines.append(self.indent('</SW-DATA-DEF-PROPS>',1))

        typeElem = ws.find(elem.typeRef, role="DataType")
        if (typeElem is None):
            raise ValueError("invalid type reference: '%s'"%elem.typeRef)
        else:
            lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(typeElem.tag(self.version),typeElem.ref),1))
        if self.version < 4.0:
            lines.append(self.indent('<IS-QUEUED>%s</IS-QUEUED>'%self.toBoolean(elem.isQueued),1))
        lines.append('</%s>'%elem.tag(self.version))
        return lines

class ElementWriter(BaseWriter, metaclass=abc.ABCMeta):

    def __init__(self, version, patch=None):
        """
        version: the XML (schema) version that this writer is expected to output. The value is the form of a float.
        E.g. version=3.0 means AUTOSAR 3.0.
        patch: Not yet supported but will eventually contain the expected patch version in the form of an integer.

        Combined Example: version=4.1, patch=1 means AUTOSAR 4.1.1
        """
        super().__init__(version, patch)

    @abc.abstractmethod
    def getSupportedXML(self):
        """
        Returns a list of class-names (strings) that this writer can turn into XML.
        A generator returning strings is also OK.
        """

    @abc.abstractmethod
    def writeElementXML(self, elem):
        """
        Invokes the XML writer, requesting it to convert the elem object into XML

        The method shall return a list of strings that contains valid XML text.

        elem: the element object to write.
        """

    @abc.abstractmethod
    def getSupportedCode(self):
        """
        Returns a list of class-names (strings) that this writer can turn into Python 3 code.
        A generator returning strings is also OK.
        """

    @abc.abstractmethod
    def writeElementCode(self, elem, localvars):
        """
        Invokes the code writer, requesting it to convert the elem object into (normalized) Python code

        The method shall return a list of strings that contains valid python3 code that, when executed recreates the elem object.

        elem: the element object to write.
        localvars: A dictionary containing local variables that the generated code can safely use.
        """
