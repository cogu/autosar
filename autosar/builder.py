import autosar.constant
import autosar.datatype
import collections
import sys

class ValueBuilder:
    """
    Builds AUTOSAR 4 value specifications from python data
    """
    def __init__(self):
        self.value = None

    def buildFromDataType(self, dataType, rawValue, name = None, ws = None, parent = None):
        assert(dataType is not None)
        if ws is None:
            ws = dataType.rootWS()
            assert(ws is not None)
        return self._createFromDataTypeInternal(ws, name, dataType, rawValue, parent)

    def _createFromDataTypeInternal(self, ws, name, dataType, rawValue, parent = None):
        if isinstance(dataType, (autosar.datatype.ImplementationDataType, autosar.datatype.ApplicationPrimitiveDataType)):
            value = None
            dataConstraint = None
            if isinstance(dataType, autosar.datatype.ImplementationDataType):
                variantProps = dataType.variantProps[0]
            if variantProps is not None:
                if variantProps.dataConstraintRef is not None:
                    dataConstraint = ws.find(variantProps.dataConstraintRef, role='DataConstraint')
                    if dataConstraint is None:
                        raise ValueError('{0.name}: Invalid DataConstraint reference: {1.dataConstraintRef}'.format(dataType, variantProps))
                if variantProps.compuMethodRef is not None:
                    compuMethod = ws.find(variantProps.compuMethodRef, role='CompuMethod')
                    if compuMethod is None:
                        raise ValueError('{0.name}: Invalid CompuMethod reference: {1.compuMethodRef}'.format(dataType, variantProps))
                    computation = compuMethod.intToPhys
                    if compuMethod.category == 'TEXTTABLE':
                        #TODO: check textValue value here
                        value = autosar.constant.TextValue(name, str(rawValue))
                    else:
                        #TODO: check rawValue here
                        value = autosar.constant.NumericalValue(name, rawValue)
            if value is None:
                if dataType.category == 'VALUE':
                    if isinstance(rawValue, str):
                        value = autosar.constant.TextValue(name, rawValue)
                    else:
                        if dataConstraint is not None:
                            dataConstraint.check_value(rawValue)
                        value = autosar.constant.NumericalValue(name, rawValue)
                elif dataType.category == 'ARRAY':
                    value = self._createArrayValueInternal(ws, name, dataType, rawValue, parent)
                elif dataType.category == 'STRUCTURE':
                    value = self._createRecordValueInternal(ws, name, dataType, rawValue, parent)
                elif dataType.category == 'TYPE_REFERENCE':
                    referencedTypeRef = dataType.getTypeReference()
                    referencedType = ws.find(referencedTypeRef, role='DataType')
                    if referencedType is None:
                        raise ValueError('Invalid reference: '+str(referencedTypeRef))
                    value = self._createFromDataTypeInternal(ws, name, referencedType, rawValue, parent)
                else:
                    raise NotImplementedError(dataType.category)
        else:
            raise NotImplementedError(type(dataType))
        return value

    def _createRecordValueInternal(self, ws, label, dataType, initValue, parent=None):
        value = autosar.constant.RecordValueAR4(label, dataType.ref, parent)
        if isinstance(initValue, collections.abc.Mapping):
            a = set() #datatype elements
            b = set() #initvalue elements
            for subElem in dataType.subElements:
                a.add(subElem.name)
            for key in initValue.keys():
                b.add(key)
            extra_keys = b-a
            if len(extra_keys) > 0:
                name_str = "" if name is None else "{}: ".format(name)
                raise ValueError('{}Unknown name(s) in initializer: {}'.format(name_str, ', '.join(extra_keys)))


            for elem in dataType.subElements:
                if elem.name in initValue:
                    v = initValue[elem.name]
                    childProps = elem.variantProps[0]
                    if childProps.implementationTypeRef is not None:
                        childTypeRef = childProps.implementationTypeRef
                    else:
                        raise NotImplementedError('could not deduce the type of element "%s"'%(elem.name))
                    childType = ws.find(childTypeRef, role='DataType')
                    if childType is None:
                        raise autosar.base.InvalidDataTypeRef(str(childTypeRef))
                    childValue = self._createFromDataTypeInternal(ws, elem.name, childType, v, value)
                    assert(childValue is not None)
                    value.elements.append(childValue)
                else:
                    name_str = "" if name is None else "{}: ".format(name)
                    raise ValueError('{}Missing initValue field: {}'.format(name_str, elem.name))
        else:
            raise ValueError('initValue must be a dict')
        return value

    def _createArrayValueInternal(self, ws, label, dataType, initValue, parent=None):
        value = autosar.constant.ArrayValueAR4(label, dataType.ref, None, parent)
        typeArrayLength = dataType.getArrayLength()
        if not isinstance(typeArrayLength, int):
            raise ValueError('dataType has no valid array length')
        if isinstance(initValue, collections.abc.Sequence):
            if isinstance(initValue, str):
                initValue = list(initValue)
                if len(initValue)<typeArrayLength:
                    #pad with zeros until length matches
                    initValue += [0]*(typeArrayLength-len(initValue))
                    assert(len(initValue) == typeArrayLength)
            if len(initValue) > typeArrayLength:
                print("%s: Excess array init values detected. Expected length=%d, got %d items"%(name, typeArrayLength, len(initValue)), file=sys.stderr)
            if len(initValue) < typeArrayLength:
                print("%s: Not enough array init values. Expected length=%d, got %d items"%(name, typeArrayLength, len(initValue)), file=sys.stderr)
            i=0
            for v in initValue:
                if isinstance(v, str):
                    value.elements.append(autosar.constant.TextValue(None, v))
                else:
                    value.elements.append(autosar.constant.NumericalValue(None, v))
                i+=1
                if i>=typeArrayLength:
                    break
        return value
