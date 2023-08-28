"""
SwBaseTypeRef example
"""
import autosar
import autosar.xml.element as ar_element


if __name__ == "__main__":

    package = ar_element.Package('BaseTypes')
    elem = ar_element.SwBaseType('uint8', size=8, native_declaration='uint8')
    package.append(elem)
    document = autosar.xml.document.Document(packages=[package])
    ref = elem.ref()
    print(str(ref))
    print(ref.dest)
