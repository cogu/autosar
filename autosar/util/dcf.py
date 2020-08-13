import ntpath
import os
import sys
import xml.etree.ElementTree as ElementTree
import autosar

dvg_xml = """<?xml version="1.0" encoding="utf-8"?>
<DVG>
	<Version>1.0</Version>
	<Contents>
	</Contents>
</DVG>"""

class XMLWriterSimple:

    def __init__(self):
        self.indentChar='\t'

    def make_dirs(self, dest_dir):
        if dest_dir != '.' and dest_dir != '..':
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

    def indent(self, lines, amount):
        if isinstance(lines, str):
            return self.indentChar*amount+lines
        elif isinstance(lines, list):
            return [self.indentChar*amount+line for line in lines]
        else:
            raise ValueError('lines must be string or list')

class DcfProfile(XMLWriterSimple):
    """
    Container for DaVinci Developer Profile Settings
    """
    def __init__(self):
        super().__init__()
        self.ExtendedShortNameLength=True
        self.DataMapping_Compatibility=True
        self.DataMapping_Defines=True
        self.DataMapping_InitValues=True
        self.DataMapping_InvalidValues = True
        self.DataMapping_Length = True
        self.DataMapping_Scale = True
        self.DataMapping_SignalGroups = True
        self.DataMapping_Unit = True
        self.DataType_UseTerminatingNullByteForStrings = False
        self.PortCompat_CheckDelegationConnectorComSpec = True
        self.SoftwareDesign_PortCompatibility = False
        self.UnconnectedPorts_Calibration = False
        self.UnconnectedPorts_ClientPorts = True
        self.UnconnectedPorts_ReceiverPorts = True
        self.UnconnectedPorts_SenderPorts = True
        self.UnconnectedPorts_ServerPorts = True
        self.ShowCalibrationObjects = False
        self.UseGraphicEditors = True
        self.DefaultPackage_DataTypes = "DataTypes"
        self.DefaultPackage_Constants = "Constants"
        self.DefaultPackage_PortInterfaces = "PortInterfaces"
        self.DefaultPackage_ComponentTypes = "ComponentTypes"
        self.DefaultPackage_ModeDeclarationGroups = "ModeDclrGroups"
        self.DefaultPackage_BaseTypes = "DataTypes/BaseTypes"
        self.DefaultPackage_Units = "DataTypes/Units"
        self.DefaultPackage_CompuMethods = "DataTypes/CompuMethods"
        self.DefaultPackage_DataConstrs = "DataTypes/DataConstrs"
        self.DefaultPackage_DataTypeMappingSets = "ComponentTypes/DataTypeMappingSets"
        self.DefaultPackage_EndToEndProtections = "EndToEndProtections"
        self.DefaultPackage_ECUCompositions = "ECUCompositions"
        self.DefaultPackage_ECUCompositionTypes = "ECUCompositionTypes"
        self.DefaultPackage_ECUProjects = "Systems"
        self.DefaultPackage_Blueprints = "Blueprints/PortPrototypeBlueprints"
        self.DefaultPackage_BlueprintMappingSets = "Blueprints/BlueprintMappingSets"
        self.DefaultPackage_SwAddrMethods = "SwAddrMethod"

        self.sectionKeys = {'AUTOSAR_XML': set(['ExtendedShortNameLength']),
                            'CHECK_AND_SYNCHRONIZE': set(['DataMapping_Compatibility',
                                                         'DataMapping_Defines',
                                                         'DataMapping_InitValues',
                                                         'DataMapping_InvalidValues',
                                                         'DataMapping_Length',
                                                         'DataMapping_Scale',
                                                         'DataMapping_SignalGroups',
                                                         'DataMapping_Unit',
                                                         'DataType_UseTerminatingNullByteForStrings',
                                                         'PortCompat_CheckDelegationConnectorComSpec',
                                                         'SoftwareDesign_PortCompatibility',
                                                         'UnconnectedPorts_Calibration',
                                                         'UnconnectedPorts_ClientPorts',
                                                         'UnconnectedPorts_ReceiverPorts',
                                                         'UnconnectedPorts_SenderPorts',
                                                         'UnconnectedPorts_ServerPorts'
                                                         ]),
                            'DEFAULT_PACKAGES': set(['DefaultPackage_DataTypes',
                                                     'DefaultPackage_Constants',
                                                     'DefaultPackage_PortInterfaces',
                                                     'DefaultPackage_ComponentTypes',
                                                     'DefaultPackage_ModeDeclarationGroups',
                                                     'DefaultPackage_BaseTypes',
                                                     'DefaultPackage_Units',
                                                     'DefaultPackage_CompuMethods',
                                                     'DefaultPackage_DataConstrs',
                                                     'DefaultPackage_DataTypeMappingSets',
                                                     'DefaultPackage_EndToEndProtections',
                                                     'DefaultPackage_ECUCompositions',
                                                     'DefaultPackage_ECUCompositionTypes',
                                                     'DefaultPackage_ECUProjects',
                                                     'DefaultPackage_Blueprints',
                                                     'DefaultPackage_BlueprintMappingSets',
                                                     'DefaultPackage_SwAddrMethods']),
                            'GRAPHIC_OBJECT_FILTER': set(['ShowCalibrationObjects', 'UseGraphicEditors']) }

    def save(self, dest_dir, force = True):
        dest_file = os.path.join(dest_dir, 'ProfileSettings.xml')
        if force or not os.path.isfile(dest_file):
            lines = ['<?xml version="1.0" encoding="utf-8"?>']
            lines.append('<PROFILE>')
            lines.append(self.indent('<Version>1.0</Version>',1))
            lines.extend(self.indent(self.gen_sections_all(),1))
            lines.append('</PROFILE>')
            with open(dest_file, 'w') as fp:
                fp.write('\n'.join(lines))
                fp.write('\n')

    def gen_sections_all(self):
        lines = []
        for name in self.sectionKeys.keys():
            section_values = {}
            for key in self.sectionKeys[name]:
                value = getattr(self, key, None)
                if value is not None:
                    section_values[key]=value
            if len(section_values)>0: #prevent generating empty sections
                lines.extend(self.gen_section(name, section_values))
        return lines

    def gen_section(self, name, section_values):
        lines = []
        lines.append('<SECTION NAME="{}">'.format(name))
        for key in sorted(section_values.keys()):
            value = section_values[key]
            if isinstance(value, bool):
                value = str(int(value))
            lines.append(self.indent('<KEYVALPAIR KEY="{}" VAL="{}" />'.format(key, value),1))
        lines.append('</SECTION>')
        return lines

class Dcf(XMLWriterSimple):
    """
    Container for DaVinci Developer configuration file (DCF).
    DaVinci 3.x not supported
    """
    def __init__(self, ws, profile = None):
        """
        Constructor
        The profile argument should be is an instance of autosar.Workspace (only used when saving DCF files)
        """
        super().__init__()
        self.file_ref = []
        self.external_file_ref = []
        self.ws = ws

        self.component_name = None
        if profile is not None:
            if not isinstance(profile, DcfProfile):
                raise ValueError("profile must be an instance of DcfProfile")
            self.profile = profile
        else:
            self.profile = DcfProfile()

    def adjust_file_refs(self, basedir):
        for elem in self.file_ref+self.external_file_ref:
            self._adjust_elem(elem, basedir)

    def _adjust_elem(self, elem, basedir):
        basename = ntpath.basename(elem['path'])
        dirname = ntpath.normpath(ntpath.join(basedir,ntpath.dirname(elem['path'])))
        elem['path']=ntpath.join(dirname,basename)
        if os.path.sep == '/': #are we running in cygwin/Linux?
            elem['path'] = elem['path'].replace(r'\\','/')

    def loadReferences(self, ws = None, external = True):
        """
        Loads ARXML from referenced files into an AUTOSAR workspace.
        Returns the workspace object.
        Parameters:

        * ws: Workspace object where ARXML will be loaded
        * external: If True it will recursively load externally referenced DCF files (DCF inside DCF)

        """
        parser = DcfParser()
        if ws is None:
            ws = autosar.workspace()
        for xml_path in [x['path'] for x in self.file_ref ]:
            ws.loadXML(xml_path)
        if external:
            for external_dcf in self.external_file_ref:
                child_path = external_dcf['path']
                if os.path.exists(child_path):
                    root, ext = os.path.splitext(child_path)
                    if ext == '.dcf':
                        child_dcf = parser.parse(child_path)
                        child_dcf.loadReferences(ws)
                else:
                    print("No such file: "+child_path, file=sys.stderr)
        return ws

    def save(self, dest_dir, dcf_name, file_map = None, comp_dir = None, force = False, single_file = None):
        """
        Saves the DaVinci Configuration to file system.
        parameters:
            dest_dir (str): Destination directory (will be automatically created if not exists)
            dcf_name: Name of the generated DCF file
            file_map: A dictionary where key is the ARXML file and value is another dictionary with two keys ('root' and 'filters')
            comp_dir: Composition directory (reserved for future use)
            force: If true, Overwrites file(s) if it already exists.
            single_file: Name of single ARXML file. Disabled usage of file_map (Not yet implemented)

        Examples of file_map:
            file_map = {'AUTOSAR_Platform': {'root': 'DATATYPE', 'filters': ['/AUTOSAR_Platform']}}

        Valid root-names in DCF (you can use the same root-name multiple times in the same DCF):

        * 'COMPONENTTYPE'
        * 'CONSTANT'
        * 'DATATYPE'
        * 'METHOD'
        * 'PACKAGE'
        * 'PORTINTERFACE'

        """
        self.make_dirs(dest_dir)
        if single_file:
            file_map = self._create_single_file_map(single_file)
        else:
            if file_map is None:
                file_map = self.create_default_file_map()
        self.save_xml_from_file_map(dest_dir, file_map, force)
        self.profile.save(dest_dir, force)
        self.save_dcf(dest_dir, dcf_name, file_map, force = force)

    def save_xml_single(self, dest_dir, file_name, force):
        raise NotImplementedError("single XML")

    def save_xml_from_file_map(self, dest_dir, xml_file_map, force):
        for key in xml_file_map.keys():
            file_name = key
            if not file_name.lower().endswith('.arxml'):
                file_name+='.arxml'
            dest_file = os.path.join(dest_dir, file_name)
            if force or not os.path.isfile(dest_file):
                elem = xml_file_map[key]
                self.ws.saveXML(dest_file, filters=elem['filters'])

    def create_default_file_map(self):
        dataTypesPackage = self.ws.findRolePackage('DataType')
        constantsPackage = self.ws.findRolePackage('Constant')
        portInterfacePackage = self.ws.findRolePackage('PortInterface')
        modeDeclarationPackage = self.ws.findRolePackage('ModeDclrGroup')
        componentTypePackage = self.ws.findRolePackage('ComponentType')
        file_map = {}
        if dataTypesPackage is not None:
            file_map['DataTypes'] = {'root': 'DATATYPE', 'filters': [dataTypesPackage.ref]}
        if constantsPackage is not None:
            file_map['Constants'] = {'root': 'CONSTANT', 'filters': [constantsPackage.ref]}
        if (portInterfacePackage is not None) or (modeDeclarationPackage is not None):
            filters = []
            if portInterfacePackage is not None:
                filters.append(portInterfacePackage.ref)
            if modeDeclarationPackage is not None:
                filters.append(modeDeclarationPackage.ref)
            file_map['PortInterfaces'] = {'root': 'PORTINTERFACE', 'filters': filters}
        if componentTypePackage is not None:
            file_map['ComponentTypes'] = {'root': 'COMPONENTTYPE', 'filters': [componentTypePackage.ref]}
        return file_map

    def save_dcf(self, dest_dir, dcf_name, xml_file_map, schema = None, force = True):
        """Generates a new DCF file. Will not overwrite existing file unless force is true"""
        file_ext = '' if dcf_name.lower().endswith('.dcf') else '.dcf'
        dest_file = os.path.join(dest_dir, dcf_name+file_ext)
        if force or not os.path.isfile(dest_file):
            lines=['<?xml version="1.0" encoding="utf-8"?>']
            if schema is None:
                #TODO: Below line needs to be improved
                schema_string = "{0}{1}_DEV".format(str(self.ws.version).replace('.',''), self.ws.patch)
            else:
                schema_string = schema
            lines.append('<DCF ARSCHEMA="{}">'.format(schema_string))
            lines.append(self.indent('<Version>1.0</Version>',1))
            lines.append(self.indent('<NAME>{}</NAME>'.format(dcf_name),1))
            lines.append(self.indent('<PROFILESETTINGS>ProfileSettings.xml</PROFILESETTINGS>',1))
            for key in xml_file_map.keys():
                elem = xml_file_map[key]
                extension = '' if key.lower().endswith('.arxml') else '.arxml'
                file_name = key + extension
                lines.extend(self.indent(self._single_file_ref(file_name),1))
            lines.append('</DCF>')
            with open(dest_file, 'w') as fp:
                fp.write('\n'.join(lines))
                fp.write('\n')

    def _component_file_ref(self, component_name):
        lines = ['<FILEREF>']
        lines.append(self.indent('<ARXML ROOTITEM="COMPONENTTYPE" TYPE="">{}.arxml</ARXML>'.format(component_name),1))
        lines.append(self.indent('<DVG>{}.dvg</DVG>'.format(component_name),1))
        lines.append('</FILEREF>')
        return lines

    def _single_file_ref(self, file_name, directory=None):
        if directory is not None:
            file_path = os.path.join(directory, file_name)
        else:
            file_path = file_name
        lines = ['<FILEREF>']
        lines.append(self.indent('<ARXML>{}</ARXML>'.format(file_path),1))
        lines.append('</FILEREF>')
        return lines

class DcfParser:
    """
    Parser a DaVinci Configuration File (DCF).
    DaVinci 3.x not supported
    """

    def parse(self, filename):
        """
        Parses file references and external file references from a DCF file
        """
        basedir = ntpath.dirname(filename)
        xml_root = self._open_xml(filename)
        dcf = self._process_xml(xml_root)
        dcf.adjust_file_refs(basedir)
        return dcf

    def _open_xml(self, filename):
        xmltree = ElementTree.ElementTree()
        xmltree.parse(filename)
        xmlroot = xmltree.getroot();
        return xmlroot

    def _process_xml(self,xmlroot):
       dcf = Dcf()
       for elem in xmlroot.findall('./FILEREF'):
           node = elem.find('./ARXML')
           root_item = node.attrib['ROOTITEM'] if 'ROOTITEM' in node.attrib else None
           dcf.file_ref.append( {'rootItem': root_item, 'path': node.text} )
       for elem in xmlroot.findall('./EXTERNALFILEREF'):
           node = elem.find('./PATH')
           dcf.external_file_ref.append( {'path': node.text} )
       return dcf
