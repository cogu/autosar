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

    def build(self, label, value):
        return self._createValueInternal(label, value)

    def _createFromDataTypeInternal(self, ws, label, dataType, rawValue, parent = None):
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
                    if compuMethod.category == 'TEXTTABLE':
                        #TODO: check textValue value here
                        value = autosar.constant.TextValue(label, str(rawValue))
                    else:
                        #TODO: check rawValue here
                        value = autosar.constant.NumericalValue(label, rawValue)
            if value is None:
                if dataType.category == 'VALUE':
                    if isinstance(rawValue, str):
                        value = autosar.constant.TextValue(label, rawValue)
                    else:
                        if dataConstraint is not None:
                            dataConstraint.checkValue(rawValue)
                        value = autosar.constant.NumericalValue(label, rawValue)
                elif dataType.category == 'ARRAY':
                    value = self._createArrayValueFromTypeInternal(ws, label, dataType, rawValue, parent)
                elif dataType.category == 'STRUCTURE':
                    value = self._createRecordValueFromTypeInternal(ws, label, dataType, rawValue, parent)
                elif dataType.category == 'TYPE_REFERENCE':
                    referencedTypeRef = dataType.getTypeReference()
                    referencedType = ws.find(referencedTypeRef, role='DataType')
                    if referencedType is None:
                        raise ValueError('Invalid reference: '+str(referencedTypeRef))
                    value = self._createFromDataTypeInternal(ws, label, referencedType, rawValue, parent)
                else:
                    raise NotImplementedError(dataType.category)
        else:
            raise NotImplementedError(type(dataType))
        return value

    def _createRecordValueFromTypeInternal(self, ws, label, dataType, initValue, parent=None):
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
                label_str = "" if label is None else "{}: ".format(label)
                raise ValueError('{}Unknown items in initializer: {}'.format(label_str, ', '.join(extra_keys)))


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
                    name_str = "" if elem.name is None else "{}: ".format(elem.name)
                    raise ValueError('{}Missing initValue field: {}'.format(name_str, elem.name))
        else:
            raise ValueError('initValue must be a dict')
        return value

    def _createArrayValueFromTypeInternal(self, ws, label, dataType, initValue, parent=None):
        value = autosar.constant.ArrayValueAR4(label, dataType.ref, None, parent)
        typeArrayLength = dataType.subElements[0].arraySize
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
                print("%s: Excess array init values detected. Expected length=%d, got %d items"%(label, typeArrayLength, len(initValue)), file=sys.stderr)
            if len(initValue) < typeArrayLength:
                print("%s: Not enough array init values. Expected length=%d, got %d items"%(label, typeArrayLength, len(initValue)), file=sys.stderr)
            i=0
            childTypeRef = dataType.subElements[0].variantProps[0].implementationTypeRef
            childType = ws.find(childTypeRef, role='DataType')
            if childType is None:
                raise autosar.base.InvalidDataTypeRef(str(childTypeRef))
            for v in initValue:
                inner_value = self._createFromDataTypeInternal(ws, None, childType, v, None)
                if inner_value is not None:
                    value.elements.append(inner_value)
                else:
                    raise RuntimeError("Failed to build value for '{}'".format(v))
                i+=1
                if i>=typeArrayLength:
                    break
        return value

    def _createValueInternal(self, label, value):
        if isinstance(value, str):
            return autosar.constant.TextValue(label, value)
        elif isinstance(value, (int, float)):
            return autosar.constant.NumericalValue(label, value)
        elif isinstance(value, collections.abc.Mapping):
            record_value = autosar.constant.RecordValueAR4(label)
            for key in value.keys():
                inner_value = value[key]
                child_value = self._createValueInternal(key, inner_value)
                if child_value is not None:
                    record_value.elements.append(child_value)
                else:
                    raise RuntimeError('Failed to build init-value for "{}"'.format(str(inner_value)))
            return record_value
        elif isinstance(value, collections.abc.Sequence):
            array_value = autosar.constant.ArrayValueAR4(label)
            for inner_value in value:
                child_value = self._createValueInternal(None, inner_value)
                if child_value is not None:
                    array_value.elements.append(child_value)
                else:
                    raise RuntimeError('Failed to build init-value for "{}"'.format(str(inner_value)))
            return array_value
        else:
            raise NotImplementedError(type(value))
