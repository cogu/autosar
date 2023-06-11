"""
SwBaseTypeRef example
"""
import autosar.xml as ar_xml
import autosar.xml.element as ar_element


if __name__ == "__main__":

    package = ar_xml.package.Package('BaseTypes')
    elem = ar_element.SwBaseType('uint8', size=8, native_declaration='uint8')
    package.append(elem)
    document = ar_xml.document.Document(packages=[package])
    ref = elem.ref()
    print(str(ref))
    print(ref.dest)
