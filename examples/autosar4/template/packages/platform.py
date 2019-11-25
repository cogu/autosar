#!/usr/bin/env python3
import autosar

enable_64_bit_types = True

class AUTOSAR_Platform(autosar.Template):

    """AUTOSAR Platform Package"""

    @classmethod
    def ref(cls): return '/AUTOSAR_Platform'

    @classmethod
    def apply(cls, ws):
        package = ws.find('/AUTOSAR_Platform')
        if package is None:
            package = ws.createPackage('AUTOSAR_Platform')
            package.createSubPackage('BaseTypes')
            package.createSubPackage('CompuMethods')
            package.createSubPackage('DataConstrs')
            package.createSubPackage('ImplementationDataTypes')

    class all(autosar.Template):
        """
        Applies all known platform templates at once
        """
        @classmethod
        def apply(self, ws):
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.dtRef_const_VOID)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.dtRef_VOID)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.boolean)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.float32)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.float64)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.sint8)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.sint16)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.sint32)
            if enable_64_bit_types:
                ws.apply(AUTOSAR_Platform.ImplementationDataTypes.sint64)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.uint8)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.uint16)
            ws.apply(AUTOSAR_Platform.ImplementationDataTypes.uint32)
            if enable_64_bit_types:
                ws.apply(AUTOSAR_Platform.ImplementationDataTypes.uint64)
            # ws.apply(AUTOSAR_Platform.BaseTypes.boolean)
            # ws.apply(AUTOSAR_Platform.BaseTypes.dtRef_const_VOID)
            # ws.apply(AUTOSAR_Platform.BaseTypes.dtRef_VOID)
            # ws.apply(AUTOSAR_Platform.BaseTypes.sint16)
            # ws.apply(AUTOSAR_Platform.BaseTypes.sint8)
            # ws.apply(AUTOSAR_Platform.BaseTypes.uint8)
            # ws.apply(AUTOSAR_Platform.BaseTypes.uint16)
            # ws.apply(AUTOSAR_Platform.BaseTypes.uint32)
            # ws.apply(AUTOSAR_Platform.BaseTypes.float32)
            # ws.apply(AUTOSAR_Platform.BaseTypes.float64)
            # ws.apply(AUTOSAR_Platform.ImplementationDataTypes.boolean)


            # ws.apply(AUTOSAR_Platform.ImplementationDataTypes.sint16)
            # ws.apply(AUTOSAR_Platform.ImplementationDataTypes.sint8)

            # ws.apply(AUTOSAR_Platform.ImplementationDataTypes.uint16)
            # ws.apply(AUTOSAR_Platform.ImplementationDataTypes.uint32)
            # ws.apply(AUTOSAR_Platform.ImplementationDataTypes.float32)


    class BaseTypes:

        @classmethod
        def ref(cls): return '/AUTOSAR_Platform/BaseTypes'

        class dtRef_const_VOID(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 1, encoding = 'VOID', nativeDeclaration = 'void')

        class dtRef_VOID(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 1, encoding = 'VOID', nativeDeclaration = 'void')


        class boolean(autosar.Template):

            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 8, encoding = 'BOOLEAN', nativeDeclaration='boolean')

        class float32(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 32, encoding = 'IEEE754', nativeDeclaration = cls.__name__)

        class float64(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 64, encoding = 'IEEE754', nativeDeclaration = cls.__name__)

        class sint8(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 8, encoding = '2C', nativeDeclaration = cls.__name__)

        class sint16(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 16, encoding = '2C', nativeDeclaration = cls.__name__)

        class sint32(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 32, encoding = '2C', nativeDeclaration = cls.__name__)

        class sint64(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 64, encoding = '2C', nativeDeclaration = cls.__name__)


        class uint8(autosar.Template):

            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 8, nativeDeclaration = cls.__name__)

        class uint16(autosar.Template):

            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 16, nativeDeclaration = cls.__name__)

        class uint32(autosar.Template):

            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 32, nativeDeclaration = cls.__name__)

        class uint64(autosar.Template):

            @classmethod
            def ref(cls): return AUTOSAR_Platform.BaseTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform)
                package = ws.find(AUTOSAR_Platform.BaseTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createSwBaseType(cls.__name__, 64, nativeDeclaration = cls.__name__)


    class ImplementationDataTypes:

        @classmethod
        def ref(cls): return '/AUTOSAR_Platform/ImplementationDataTypes'

        class dtRef_const_VOID(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.dtRef_const_VOID)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createImplementationDataTypePtr(cls.__name__, AUTOSAR_Platform.BaseTypes.dtRef_const_VOID.ref(), swImplPolicy = 'CONST')

        class dtRef_VOID(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.dtRef_VOID)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    package.createImplementationDataTypePtr(cls.__name__, AUTOSAR_Platform.BaseTypes.dtRef_VOID.ref())

        class boolean(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.boolean)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.boolean.ref(), valueTable=['FALSE', 'TRUE'], typeEmitter='Platform_Type')
                    ws.popRoles()

        class float32(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.float32)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.float32.ref(), lowerLimit="-INF", lowerLimitType="OPEN", upperLimit="INF", upperLimitType="OPEN", typeEmitter='Platform_Type')
                    ws.popRoles()

        class float64(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.float64)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.float64.ref(), lowerLimit="-INF", lowerLimitType="OPEN", upperLimit="INF", upperLimitType="OPEN", typeEmitter='Platform_Type')
                    ws.popRoles()

        class sint8(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.sint8)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.sint8.ref(), lowerLimit=-128, upperLimit=127, typeEmitter='Platform_Type')
                    ws.popRoles()

        class sint16(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.sint16)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.sint16.ref(), lowerLimit=-32768, upperLimit=32767, typeEmitter='Platform_Type')
                    ws.popRoles()

        class sint32(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.sint32)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.sint32.ref(), lowerLimit=-2147483648, upperLimit=2147483647, typeEmitter='Platform_Type')
                    ws.popRoles()

        class sint64(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.sint64)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.sint64.ref(), lowerLimit=-9223372036854775808, upperLimit=9223372036854775807, typeEmitter='Platform_Type')
                    ws.popRoles()

        class uint8(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.uint8)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.uint8.ref(), lowerLimit=0, upperLimit=255, typeEmitter='Platform_Type')
                    ws.popRoles()

        class uint16(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.uint16)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.uint16.ref(), lowerLimit=0, upperLimit=65535, typeEmitter='Platform_Type')
                    ws.popRoles()

        class uint32(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.uint32)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.uint32.ref(), lowerLimit=0, upperLimit=4294967295, typeEmitter='Platform_Type')
                    ws.popRoles()

        class uint64(autosar.Template):
            @classmethod
            def ref(cls): return AUTOSAR_Platform.ImplementationDataTypes.ref() + '/' + cls.__name__

            @classmethod
            def apply(cls, ws):
                ws.apply(AUTOSAR_Platform.BaseTypes.uint64)
                package = ws.find(AUTOSAR_Platform.ImplementationDataTypes.ref())
                if package.find(cls.__name__) is None:
                    ws.pushRoles()
                    ws.setRoles(('/AUTOSAR_Platform/CompuMethods', 'CompuMethod'), ('/AUTOSAR_Platform/DataConstrs', 'DataConstraint'))
                    package.createImplementationDataType(cls.__name__, AUTOSAR_Platform.BaseTypes.uint64.ref(), lowerLimit=0, upperLimit=18446744073709551615, typeEmitter='Platform_Type')
                    ws.popRoles()


if __name__ == '__main__':
    ws = autosar.workspace("4.2.2")
    ws.apply(AUTOSAR_Platform.all)
    autosar.util.createDcf(ws).save('autosar4', 'Platform', {
        'AUTOSAR_Platform': {'root': 'DATATYPE', 'filters': ['/AUTOSAR_Platform']}
        }, force=True)
