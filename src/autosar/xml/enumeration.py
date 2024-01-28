"""
Enum Definitions
"""

from enum import Enum

# from typing import Any
from dataclasses import dataclass
import autosar.base as ar_base
import autosar.xml.exception as ar_exception


class ArrayImplPolicy(Enum):
    """
    AR:ARRAY-IMPL-POLICY-ENUM--SIMPLE
    """

    PAYLOAD_AS_ARRAY = 0
    PAYLOAD_AS_POINTER_TO_ARRAY = 1


class ArraySizeHandling(Enum):
    """
    AR:ARRAY-SIZE-HANDLING-ENUM--SIMPLE
    """

    ALL_INDICES_DIFFERENT_ARRAY_SIZE = 0
    ALL_INDICES_SAME_ARRAY_SIZE = 1
    INHERITED_FROM_ARRAY_ELEMENT_TYPE_SIZE = 2


class ArraySizeSemantics(Enum):
    """
    AR:ARRAY-SIZE-SEMANTICS-ENUM--SIMPLE
    """

    FIXED_SIZE = 0
    VARIABLE_SIZE = 1


class ByteOrder(Enum):
    """
    BYTE-ORDER-ENUM
    Note: The XML schema uses phrasing such as
    "most significant byte first" but we will
    instead use the most recognized terminology
    amongst software developers.
    """

    BIG_ENDIAN = 0
    LITTLE_ENDIAN = 1
    OPAQUE = 2


class CalibrationAxisCategory(Enum):
    """
    AR:CALPRM-AXIS-CATEGORY-ENUM--SIMPLE

    For some reason the XML schema defines the
    values of this eanum with both '_' and '-' separators.
    Seems like a mistake.
    """

    COM_AXIS = 0
    CURVE_AXIS = 1
    FIX_AXIS = 2
    RES_AXIS = 3
    STD_AXIS = 4


class CompuScaleContent(Enum):
    """
    Used internally to differentiate the
    content type of CompuScale elements
    """

    NONE = 0      # No content
    CONSTANT = 1  # Content is AR:COMPU-SCALE-CONSTANT-CONTENTS
    RATIONAL = 2  # Content is COMPU-SCALE-RATIONAL-FORMULA


# class CompuType(Enum):
#     """
#     Used internally to
#     differentate what type a Computaion has
#     """

#     NONE = 0
#     INT_TO_PHYS = 1
#     PHYS_TO_INT = 2
#     BOTH = 3


class DisplayPresentation(Enum):
    """DISPLAY-PRESENTATION-ENUM"""

    CONTINUOUS = 0
    DISCRETE = 1


class EmphasisType(Enum):
    """
    E-ENUM--SIMPLE
    """

    BOLD = 0
    BOLDITALIC = 1
    ITALIC = 2
    PLAIN = 3


class EmphasisFont(Enum):
    """
    E-ENUM-FONT--SIMPLE
    """

    DEFAULT = 0
    MONO = 1


class Float(Enum):
    """
    FLOAT-ENUM--SIMPLE
    """

    FLOAT = 0
    NO_FLOAT = 1


class HandleInvalid(Enum):
    """
    HANDLE-INVALID-ENUM--SIMPLE
    """

    DONT_INVALIDATE = 0
    EXTERNAL_REPLACEMENT = 1
    KEEP = 2
    REPLACE = 3


class IdentifiableSubTypes(Enum):
    """
    IDENTIFIABLE--SUBTYPES-ENUM

    This is just a small subset.
    More items will be added as implementation progresses.
    """

    ABSTRACT_IMPLEMENTATION_DATA_TYPE = 0
    APPLICATION_ARRAY_DATA_TYPE = 1
    APPLICATION_ASSOC_MAP_DATA_TYPE = 2
    APPLICATION_COMPOSITE_DATA_TYPE = 3
    APPLICATION_DATA_TYPE = 4
    APPLICATION_DEFERRED_DATA_TYPE = 5
    APPLICATION_PRIMITIVE_DATA_TYPE = 6
    APPLICATION_RECORD_DATA_TYPE = 7
    AUTOSAR_DATA_TYPE = 8
    BSW_MODULE_ENTRY = 9
    COMPU_METHOD = 10
    CONSTANT_SPECIFICATION = 11
    DATA_CONSTR = 12
    IMPLEMENTATION_DATA_TYPE = 13
    PHYSICAL_DIMENSION = 14
    SW_ADDR_METHOD = 15
    SW_BASE_TYPE = 16
    UNIT = 17
    VARIABLE_DATA_PROTOTYPE = 18


class IntervalType(Enum):
    """
    INTERVAL-TYPE-ENUM--SIMPLE

    Don't include INFINITE as it's been marked obsolete.
    """

    CLOSED = 0
    OPEN = 1


class KeepWithPrevious(Enum):
    """
    AR:KEEP-WITH-PREVIOUS-ENUM--SIMPLE
    """

    KEEP = 0
    NO_KEEP = 1


class Language(Enum):
    """
    SimpleType AR:L-ENUM--SIMPLE
    """

    AA = 0  # Afar
    AB = 1  # Abkhazian
    AF = 2  # Afrikaans
    AM = 3  # Amharic
    AR = 4  # Arabic
    AS = 5  # Assamese
    AY = 6  # Aymara
    AZ = 7  # Azerbaijani
    BA = 8  # Bashkir
    BE = 9  # Byelorussian
    BG = 10  # Bulgarian
    BH = 11  # Bihari
    BI = 12  # Bislama
    BN = 13  # Bengali
    BO = 14  # Tibetian
    BR = 15  # Breton
    CA = 16  # Catalan
    CO = 17  # Corsican
    CS = 18  # Czech
    CY = 19  # Welsh
    DA = 20  # Danish
    DE = 21  # German
    DZ = 22  # Bhutani
    EL = 23  # Greek
    EN = 24  # English
    EO = 25  # Esperanto
    ES = 26  # Spanish
    ET = 27  # Estonian
    EU = 28  # Basque
    FA = 29  # Persian
    FI = 30  # Finnish
    FJ = 31  # Fiji
    FO = 32  # Faeroese
    FOR_ALL = 33  # All languages
    FR = 34  # French
    FY = 35  # Frisian
    GA = 36  # Irish
    GD = 37  # Scots Gaelic
    GL = 38  # Galician
    GN = 39  # Guarani
    GU = 40  # Gjarati
    HA = 41  # Hausa
    HI = 42  # Hindi
    HR = 43  # Croatian
    HU = 44  # Hungarian
    HY = 45  # Armenian
    IA = 46  # Interlingua
    IE = 47  # Interlingue
    IK = 48  # Inupiak
    IN = 49  # Indonesian
    IS = 50  # Icelandic
    IT = 51  # Italian
    IW = 52  # Hebrew
    JA = 53  # Japanese
    JI = 54  # Yiddish
    JW = 55  # Javanese
    KA = 56  # Georgian
    KK = 57  # Kazakh
    KL = 58  # Greenlandic
    KM = 59  # Cambodian
    KN = 60  # Kannada
    KO = 61  # Korean
    KS = 62  # Kashmiri
    KU = 63  # Kurdish
    KY = 64  # Kirghiz
    LA = 65  # Latin
    LN = 66  # Lingala
    LO = 67  # Laothian
    LT = 68  # Lithuanian
    LV = 69  # Lavian, Lettish
    MG = 70  # Malagasy
    MI = 71  # Maori
    MK = 72  # Macedonian
    ML = 73  # Malayalam
    MN = 74  # Mongolian
    MO = 75  # Moldavian
    MR = 76  # Marathi
    MS = 77  # Malay
    MT = 78  # Maltese
    MY = 79  # Burmese
    NA = 80  # Nauru
    NE = 81  # Nepali
    NL = 82  # Dutch
    NO = 83  # Norwegian
    OC = 84  # Occitan
    OM = 85  # (Afan) Oromo
    OR = 86  # Oriya
    PA = 87  # Punjabi
    PL = 88  # Polish
    PS = 89  # Pashto, Pushto
    PT = 90  # Portuguese
    QU = 91  # Quechua
    RM = 92  # Rhaeto-Romance
    RN = 93  # Kirundi
    RO = 94  # Romanian
    RU = 95  # Russian
    RW = 96  # Kinyarwanda
    SA = 97  # Sanskrit
    SD = 98  # Sindhi
    SG = 99  # Sangro
    SH = 100  # Serbo-Croatian
    SI = 101  # Singhalese
    SK = 102  # Slovak
    SL = 103  # Slovenian
    SM = 104  # Samoan
    SN = 105  # Shona
    SO = 106  # Somali
    SQ = 107  # Albanian
    SR = 108  # Serbian
    SS = 109  # Siswati
    ST = 110  # Sesotho
    SU = 111  # Sundanese
    SV = 112  # Swedish
    SW = 113  # Swahili
    TA = 114  # Tamil
    TE = 115  # Tegulu
    TG = 116  # Tajik
    TH = 117  # Thai
    TI = 118  # Tigrinya
    TK = 119  # Turkmen
    TL = 120  # Tagalog
    TN = 121  # Setswana
    TO = 122  # Tonga
    TR = 123  # Turkish
    TS = 124  # Tsonga
    TT = 125  # Tatar
    TW = 126  # Twi
    UK = 127  # Ukrainian
    UR = 128  # Urdu
    UZ = 129  # Uzbek
    VI = 130  # Vietnamese
    VO = 131  # Volapuk
    WO = 132  # Wolof
    XH = 133  # Xhosa
    YO = 134  # Yoruba
    ZH = 135  # Chinese
    ZU = 136  # Zulu


class Monotony(Enum):
    """
    AR:MONOTONY-ENUM--SIMPLE"
    """

    DECREASING = 0
    INCREASING = 1
    MONOTONOUS = 2
    NO_MONOTONY = 3
    STRICTLY_DECREASING = 4
    STRICTLY_INCREASING = 5
    STRICT_MONOTONOUS = 6


class PackageRole(Enum):
    """
    Supported package roles
    """

    APPLICATION_DATA_TYPE = 0
    BASE_TYPE = 1
    COMPONENT_TYPE = 2
    COMPU_METHOD = 3
    DATA_CONSTRAINT = 4
    IMPLEMENTATION_DATA_TYPE = 5
    MODE_DECLARATION_GROUP = 6
    PORT_INTERFACE = 7
    UNIT = 8
    VALUE_SPECIFICATION = 9


class PageBreak(Enum):
    """
    AR:CHAPTER-ENUM-BREAK--SIMPLE
    """

    BREAK = 0
    NO_BREAK = 1


class PageWide(Enum):
    """
    AR:PGWIDE-ENUM--SIMPLE
    """

    NO_PGWIDE = 0
    PGWIDE = 1


class ScaleConstraintValidity(Enum):
    """
    AR:SCALE-CONSTR-VALIDITY-ENUM--SIMPLE
    """

    NOT_AVAILABLE = 0
    NOT_DEFINED = 1
    NOT_VALID = 2
    VALID = 3


class ServiceKind(Enum):
    """
    SERVICE-PROVIDER-ENUM--SIMPLE
    """

    ANY_STANDARDIZED = 0
    BASIC_SOFTWARE_MODE_MANAGER = 1
    COM_MANAGER = 2
    CRYPTO_KEY_MANAGEMENT = 23
    CRYPTO_SERVICE_MANAGER = 3
    DEFAULT_ERROR_TRACER = 4
    DEVELOPMENT_ERROR_TRACER = 5
    DIAGNOSTIC_COMMUNICATION_MANAGER = 6
    DIAGNOSTIC_EVENT_MANAGER = 7
    DIAGNOSTIC_LOG_AND_TRACE = 8
    ECU_MANAGER = 9
    ERROR_TRACER = 18
    FUNCTION_INHIBITION_MANAGER = 10
    HARDWARE_TEST_MANAGER = 19
    INTRUSION_DETECTION_SECURITY_MANAGEMENT = 24
    J1939_DCM = 22
    J1939_REQUEST_MANAGER = 11
    NON_VOLATILE_RAM_MANAGER = 12
    OPERATING_SYSTEM = 13
    SECURE_ON_BOARD_COMMUNICATION = 14
    SYNC_BASE_TIME_MANAGER = 15
    V2X_FACILITIES = 20
    V2X_MANAGEMENT = 21
    VENDOR_SPECIFIC = 16
    WATCH_DOG_MANAGER = 17


class SwCalibrationAccess(Enum):
    """
    AR:SW-CALIBRATION-ACCESS-ENUM--SIMPLE
    """

    NOT_ACCESSIBLE = 0
    READ_ONLY = 1
    READ_WRITE = 2


class SwImplPolicy(Enum):
    """
    AR:SW-IMPL-POLICY-ENUM
    """

    CONST = 0
    FIXED = 1
    MEASUREMENT_POINT = 2
    QUEUED = 3
    STANDARD = 4


class ValueFormat(Enum):
    """
    Specifies the value format to use
    when writing XML (for the associated
    value).
    """

    DEFAULT = 0  # Let Python decide the format
    DECIMAL = 1
    HEXADECIMAL = 2
    BINARY = 3
    SCIENTIFIC = 4


class VariableDataPrototype(Enum):
    """
    AR:VARIABLE-DATA-PROTOTYPE--SUBTYPES-ENUM
    """


########################################


@dataclass
class VersionedEnumValue:
    """
    Versioned enumeration value
    """

    value: Enum
    valid_versions: set


@dataclass
class VersionedTextValue:
    """
    Versioned text value
    """

    value: str
    valid_versions: set


####
# Mapping between xml element and enumeratios
# Top level is the enumeration class
# Second level maps XML tags to instances
# of VersionedEnumValue.
# This keeps track of which enum values are valid in each AUTOSAR Schema version.
###

xml_to_enum_map = {
    "ArrayImplPolicy": {
        "PAYLOAD-AS-ARRAY": VersionedEnumValue(ArrayImplPolicy.PAYLOAD_AS_ARRAY, {49, 50, 51}),
        "PAYLOAD-AS-POINTER-TO-ARRAY": VersionedEnumValue(ArrayImplPolicy.PAYLOAD_AS_POINTER_TO_ARRAY, {49, 50, 51}),
    },
    "ArraySizeHandling": {
        "ALL-INDICES-DIFFERENT-ARRAY-SIZE": ArraySizeHandling.ALL_INDICES_DIFFERENT_ARRAY_SIZE,
        "ALL-INDICES-SAME-ARRAY-SIZE": ArraySizeHandling.ALL_INDICES_SAME_ARRAY_SIZE,
        "INHERITED-FROM-ARRAY-ELEMENT-TYPE-SIZE": ArraySizeHandling.INHERITED_FROM_ARRAY_ELEMENT_TYPE_SIZE
    },
    "ArraySizeSemantics": {
        "FIXED-SIZE": ArraySizeSemantics.FIXED_SIZE,
        "VARIABLE-SIZE": ArraySizeSemantics.VARIABLE_SIZE
    },
    "ByteOrder": {
        "MOST-SIGNIFICANT-BYTE-FIRST": ByteOrder.BIG_ENDIAN,
        "MOST-SIGNIFICANT-BYTE-LAST": ByteOrder.LITTLE_ENDIAN,
        "OPAQUE": ByteOrder.OPAQUE,
    },
    "CalibrationAxisCategory": {
        "COM_AXIS": CalibrationAxisCategory.COM_AXIS,
        "COM-AXIS": CalibrationAxisCategory.COM_AXIS,
        "CURVE_AXIS": CalibrationAxisCategory.CURVE_AXIS,
        "CURVE-AXIS": CalibrationAxisCategory.CURVE_AXIS,
        "FIX_AXIS": CalibrationAxisCategory.FIX_AXIS,
        "FIX-AXIS": CalibrationAxisCategory.FIX_AXIS,
        "RES_AXIS": CalibrationAxisCategory.RES_AXIS,
        "RES-AXIS": CalibrationAxisCategory.RES_AXIS,
        "STD_AXIS": CalibrationAxisCategory.STD_AXIS,
        "STD-AXIS": CalibrationAxisCategory.STD_AXIS,
    },
    "DisplayPresentation": {
        "PRESENTATION-CONTINUOUS": DisplayPresentation.CONTINUOUS,
        "PRESENTATION-DISCRETE": DisplayPresentation.DISCRETE
    },
    "EmphasisFont": {
        "DEFAULT": EmphasisFont.DEFAULT,
        "MONO": EmphasisFont.MONO,
    },
    "EmphasisType": {
        "BOLD": EmphasisType.BOLD,
        "BOLDITALIC": EmphasisType.BOLDITALIC,
        "ITALIC": EmphasisType.ITALIC,
        "PLAIN": EmphasisType.PLAIN,
    },
    "Float": {
        "FLOAT": Float.FLOAT,
        "NO-FLOAT": Float.NO_FLOAT,
    },
    "HandleInvalid": {
        "DONT-INVALIDATE": HandleInvalid.DONT_INVALIDATE,
        "EXTERNAL-REPLACEMENT": HandleInvalid.EXTERNAL_REPLACEMENT,
        "KEEP": HandleInvalid.KEEP,
        "REPLACE": HandleInvalid.REPLACE,
    },
    "IdentifiableSubTypes": {
        "ABSTRACT-IMPLEMENTATION-DATA-TYPE": IdentifiableSubTypes.ABSTRACT_IMPLEMENTATION_DATA_TYPE,
        "APPLICATION-ARRAY-DATA-TYPE": IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE,
        "APPLICATION-ASSOC-MAP-DATA-TYPE": IdentifiableSubTypes.APPLICATION_ASSOC_MAP_DATA_TYPE,
        "APPLICATION-COMPOSITE-DATA-TYPE": IdentifiableSubTypes.APPLICATION_COMPOSITE_DATA_TYPE,
        "APPLICATION-DATA-TYPE": IdentifiableSubTypes.APPLICATION_DATA_TYPE,
        "APPLICATION-DEFERRED-DATA-TYPE": IdentifiableSubTypes.APPLICATION_DEFERRED_DATA_TYPE,
        "APPLICATION-PRIMITIVE-DATA-TYPE": IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE,
        "APPLICATION-RECORD-DATA-TYPE": IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE,
        "AUTOSAR-DATA-TYPE": IdentifiableSubTypes.AUTOSAR_DATA_TYPE,
        "BSW-MODULE-ENTRY": IdentifiableSubTypes.BSW_MODULE_ENTRY,
        "COMPU-METHOD": IdentifiableSubTypes.COMPU_METHOD,
        "CONSTANT-SPECIFICATION": IdentifiableSubTypes.CONSTANT_SPECIFICATION,
        "DATA-CONSTR": IdentifiableSubTypes.DATA_CONSTR,
        "IMPLEMENTATION-DATA-TYPE": IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE,
        "PHYSICAL-DIMENSION": IdentifiableSubTypes.PHYSICAL_DIMENSION,
        "SW-ADDR-METHOD": IdentifiableSubTypes.SW_ADDR_METHOD,
        "SW-BASE-TYPE": IdentifiableSubTypes.SW_BASE_TYPE,
        "UNIT": IdentifiableSubTypes.UNIT,
        "VARIABLE-DATA-PROTOTYPE": IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE,
    },
    "IntervalType": {
        "CLOSED": IntervalType.CLOSED,
        "OPEN": IntervalType.OPEN
    },
    "KeepWithPrevious": {
        "KEEP": KeepWithPrevious.KEEP,
        "NO-KEEP": KeepWithPrevious.NO_KEEP,
    },
    "Language": {
        "AA": Language.AA,
        "AB": Language.AB,
        "AF": Language.AF,
        "AM": Language.AM,
        "AR": Language.AR,
        "AS": Language.AS,
        "AY": Language.AY,
        "AZ": Language.AZ,
        "BA": Language.BA,
        "BE": Language.BE,
        "BG": Language.BG,
        "BH": Language.BH,
        "BI": Language.BI,
        "BN": Language.BN,
        "BO": Language.BO,
        "BR": Language.BR,
        "CA": Language.CA,
        "CO": Language.CO,
        "CS": Language.CS,
        "CY": Language.CY,
        "DA": Language.DA,
        "DE": Language.DE,
        "DZ": Language.DZ,
        "EL": Language.EL,
        "EN": Language.EN,
        "EO": Language.EO,
        "ES": Language.ES,
        "ET": Language.ET,
        "EU": Language.EU,
        "FA": Language.FA,
        "FI": Language.FI,
        "FJ": Language.FJ,
        "FO": Language.FO,
        "FOR-ALL": Language.FOR_ALL,
        "FR": Language.FR,
        "FY": Language.FY,
        "GA": Language.GA,
        "GD": Language.GD,
        "GL": Language.GL,
        "GN": Language.GN,
        "GU": Language.GU,
        "HA": Language.HA,
        "HI": Language.HI,
        "HR": Language.HR,
        "HU": Language.HU,
        "HY": Language.HY,
        "IA": Language.IA,
        "IE": Language.IE,
        "IK": Language.IK,
        "IN": Language.IN,
        "IS": Language.IS,
        "IT": Language.IT,
        "IW": Language.IW,
        "JA": Language.JA,
        "JI": Language.JI,
        "JW": Language.JW,
        "KA": Language.KA,
        "KK": Language.KK,
        "KL": Language.KL,
        "KM": Language.KM,
        "KN": Language.KN,
        "KO": Language.KO,
        "KS": Language.KS,
        "KU": Language.KU,
        "KY": Language.KY,
        "LA": Language.LA,
        "LN": Language.LN,
        "LO": Language.LO,
        "LT": Language.LT,
        "LV": Language.LV,
        "MG": Language.MG,
        "MI": Language.MI,
        "MK": Language.MK,
        "ML": Language.ML,
        "MN": Language.MN,
        "MO": Language.MO,
        "MR": Language.MR,
        "MS": Language.MS,
        "MT": Language.MT,
        "MY": Language.MY,
        "NA": Language.NA,
        "NE": Language.NE,
        "NL": Language.NL,
        "NO": Language.NO,
        "OC": Language.OC,
        "OM": Language.OM,
        "OR": Language.OR,
        "PA": Language.PA,
        "PL": Language.PL,
        "PS": Language.PS,
        "PT": Language.PT,
        "QU": Language.QU,
        "RM": Language.RM,
        "RN": Language.RN,
        "RO": Language.RO,
        "RU": Language.RU,
        "RW": Language.RW,
        "SA": Language.SA,
        "SD": Language.SD,
        "SG": Language.SG,
        "SH": Language.SH,
        "SI": Language.SI,
        "SK": Language.SK,
        "SL": Language.SL,
        "SM": Language.SM,
        "SN": Language.SN,
        "SO": Language.SO,
        "SQ": Language.SQ,
        "SR": Language.SR,
        "SS": Language.SS,
        "ST": Language.ST,
        "SU": Language.SU,
        "SV": Language.SV,
        "SW": Language.SW,
        "TA": Language.TA,
        "TE": Language.TE,
        "TG": Language.TG,
        "TH": Language.TH,
        "TI": Language.TI,
        "TK": Language.TK,
        "TL": Language.TL,
        "TN": Language.TN,
        "TO": Language.TO,
        "TR": Language.TR,
        "TS": Language.TS,
        "TT": Language.TT,
        "TW": Language.TW,
        "UK": Language.UK,
        "UR": Language.UR,
        "UZ": Language.UZ,
        "VI": Language.VI,
        "VO": Language.VO,
        "WO": Language.WO,
        "XH": Language.XH,
        "YO": Language.YO,
        "ZH": Language.ZH,
        "ZU": Language.ZU,
    },
    "Monotony": {
        "DECREASING": Monotony.DECREASING,
        "INCREASING": Monotony.INCREASING,
        "MONOTONOUS": Monotony.MONOTONOUS,
        "NO-MONOTONY": Monotony.NO_MONOTONY,
        "STRICTLY-DECREASING": Monotony.STRICTLY_DECREASING,
        "STRICTLY-INCREASING": Monotony.STRICTLY_INCREASING,
        "STRICT-MONOTONOUS": Monotony.STRICT_MONOTONOUS,
    },
    "PageBreak": {
        "BREAK": PageBreak.BREAK,
        "NO-BREAK": PageBreak.NO_BREAK,
    },
    "PageWide": {
        "NO-PGWIDE": PageWide.NO_PGWIDE,
        "PGWIDE": PageWide.PGWIDE,
    },
    "ScaleConstraintValidity": {
        "NOT-AVAILABLE": ScaleConstraintValidity.NOT_AVAILABLE,
        "NOT-DEFINED": ScaleConstraintValidity.NOT_DEFINED,
        "NOT-VALID": ScaleConstraintValidity.NOT_VALID,
        "VALID": ScaleConstraintValidity.VALID
    },
    "SwCalibrationAccess": {
        "NOT-ACCESSIBLE": SwCalibrationAccess.NOT_ACCESSIBLE,
        "READ-ONLY": SwCalibrationAccess.READ_ONLY,
        "READ-WRITE": SwCalibrationAccess.READ_WRITE,
    },
    "SwImplPolicy": {
        "CONST": SwImplPolicy.CONST,
        "FIXED": SwImplPolicy.FIXED,
        "MEASUREMENT-POINT": SwImplPolicy.MEASUREMENT_POINT,
        "QUEUED": SwImplPolicy.QUEUED,
        "STANDARD": SwImplPolicy.STANDARD
    }
}


def xml_to_enum(enum_type_name: str, xml_text: str, schema_version: int = ar_base.DEFAULT_SCHEMA_VERSION) -> Enum:
    """
    Converts XML string to Python-defined enumeration
    """
    enum_mapping = xml_to_enum_map[enum_type_name]
    entry = enum_mapping[xml_text]
    if isinstance(entry, Enum):
        return entry
    elif isinstance(entry, VersionedEnumValue):
        if schema_version not in entry.valid_versions:
            raise ar_exception.VersionError(f"'{xml_text}'")
        return entry.value
    else:
        raise NotImplementedError(str(type(entry)))


# Mapping from enum back to XML string


enum_to_xml_map = {
    "ArrayImplPolicy": [
        VersionedTextValue("PAYLOAD-AS-ARRAY", {49, 50, 51}),             # 0
        VersionedTextValue("PAYLOAD-AS-POINTER-TO-ARRAY", {49, 50, 51}),  # 1
    ],
    "ArraySizeHandling": [
        "ALL-INDICES-DIFFERENT-ARRAY-SIZE",       # 0
        "ALL-INDICES-SAME-ARRAY-SIZE",            # 1
        "INHERITED-FROM-ARRAY-ELEMENT-TYPE-SIZE"  # 2
    ],
    "ArraySizeSemantics": [
        "FIXED-SIZE",     # 0
        "VARIABLE-SIZE",  # 1
    ],
    "ByteOrder": [
        "MOST-SIGNIFICANT-BYTE-FIRST",  # 0
        "MOST-SIGNIFICANT-BYTE-LAST",   # 1
        "OPAQUE",                       # 2
    ],
    "CalibrationAxisCategory": [
        "COM-AXIS",    # 0
        "CURVE-AXIS",  # 1
        "FIX-AXIS",    # 2
        "RES-AXIS",    # 3
        "STD-AXIS"     # 4
    ],
    "DisplayPresentation": [
        "PRESENTATION-CONTINUOUS",  # 0
        "PRESENTATION-DISCRETE",    # 1
    ],
    "EmphasisFont": [
        "DEFAULT",  # 0
        "MONO",     # 1
    ],
    "EmphasisType": [
        "BOLD",        # 0
        "BOLDITALIC",  # 1
        "ITALIC",      # 2
        "PLAIN",       # 3
    ],
    "Float": [
        "FLOAT",     # 0
        "NO-FLOAT",  # 1
    ],
    "HandleInvalid": [
        "DONT-INVALIDATE",       # 0
        "EXTERNAL-REPLACEMENT",  # 1
        "KEEP",                  # 2
        "REPLACE",               # 3
    ],
    "IdentifiableSubTypes": [
        "ABSTRACT-IMPLEMENTATION-DATA-TYPE",  # 0
        "APPLICATION-ARRAY-DATA-TYPE",        # 1
        "APPLICATION-ASSOC-MAP-DATA-TYPE",    # 2
        "APPLICATION-COMPOSITE-DATA-TYPE",    # 3
        "APPLICATION-DATA-TYPE",              # 4
        "APPLICATION-DEFERRED-DATA-TYPE",     # 5
        "APPLICATION-PRIMITIVE-DATA-TYPE",    # 6
        "APPLICATION-RECORD-DATA-TYPE",       # 7
        "AUTOSAR-DATA-TYPE",                  # 8
        "BSW-MODULE-ENTRY",                   # 9
        "COMPU-METHOD",                       # 10
        "CONSTANT-SPECIFICATION",             # 11
        "DATA-CONSTR",                        # 12
        "IMPLEMENTATION-DATA-TYPE",           # 13
        "PHYSICAL-DIMENSION",                 # 14
        "SW-ADDR-METHOD",                     # 15
        "SW-BASE-TYPE",                       # 16
        "UNIT",                               # 17
        "VARIABLE-DATA-PROTOTYPE"             # 18
    ],
    "IntervalType": [
        "CLOSED",  # 0
        "OPEN"  # 1
    ],
    "KeepWithPrevious": [
        "KEEP",  # 0
        "NO-KEEP",  # 1
    ],
    "Language": [
        "AA",  # 0
        "AB",  # 1
        "AF",  # 2
        "AM",  # 3
        "AR",  # 4
        "AS",  # 5
        "AY",  # 6
        "AZ",  # 7
        "BA",  # 8
        "BE",  # 9
        "BG",  # 10
        "BH",  # 11
        "BI",  # 12
        "BN",  # 13
        "BO",  # 14
        "BR",  # 15
        "CA",  # 16
        "CO",  # 17
        "CS",  # 18
        "CY",  # 19
        "DA",  # 20
        "DE",  # 21
        "DZ",  # 22
        "EL",  # 23
        "EN",  # 24
        "EO",  # 25
        "ES",  # 26
        "ET",  # 27
        "EU",  # 28
        "FA",  # 29
        "FI",  # 30
        "FJ",  # 31
        "FO",  # 32
        "FOR-ALL",  # 33
        "FR",  # 34
        "FY",  # 35
        "GA",  # 36
        "GD",  # 37
        "GL",  # 38
        "GN",  # 39
        "GU",  # 40
        "HA",  # 41
        "HI",  # 42
        "HR",  # 43
        "HU",  # 44
        "HY",  # 45
        "IA",  # 46
        "IE",  # 47
        "IK",  # 48
        "IN",  # 49
        "IS",  # 50
        "IT",  # 51
        "IW",  # 52
        "JA",  # 53
        "JI",  # 54
        "JW",  # 55
        "KA",  # 56
        "KK",  # 57
        "KL",  # 58
        "KM",  # 59
        "KN",  # 60
        "KO",  # 61
        "KS",  # 62
        "KU",  # 63
        "KY",  # 64
        "LA",  # 65
        "LN",  # 66
        "LO",  # 67
        "LT",  # 68
        "LV",  # 69
        "MG",  # 70
        "MI",  # 71
        "MK",  # 72
        "ML",  # 73
        "MN",  # 74
        "MO",  # 75
        "MR",  # 76
        "MS",  # 77
        "MT",  # 78
        "MY",  # 79
        "NA",  # 80
        "NE",  # 81
        "NL",  # 82
        "NO",  # 83
        "OC",  # 84
        "OM",  # 85
        "OR",  # 86
        "PA",  # 87
        "PL",  # 88
        "PS",  # 89
        "PT",  # 90
        "QU",  # 91
        "RM",  # 92
        "RN",  # 93
        "RO",  # 94
        "RU",  # 95
        "RW",  # 96
        "SA",  # 97
        "SD",  # 98
        "SG",  # 99
        "SH",  # 100
        "SI",  # 101
        "SK",  # 102
        "SL",  # 103
        "SM",  # 104
        "SN",  # 105
        "SO",  # 106
        "SQ",  # 107
        "SR",  # 108
        "SS",  # 109
        "ST",  # 110
        "SU",  # 111
        "SV",  # 112
        "SW",  # 113
        "TA",  # 114
        "TE",  # 115
        "TG",  # 116
        "TH",  # 117
        "TI",  # 118
        "TK",  # 119
        "TL",  # 120
        "TN",  # 121
        "TO",  # 122
        "TR",  # 123
        "TS",  # 124
        "TT",  # 125
        "TW",  # 126
        "UK",  # 127
        "UR",  # 128
        "UZ",  # 129
        "VI",  # 130
        "VO",  # 131
        "WO",  # 132
        "XH",  # 133
        "YO",  # 134
        "ZH",  # 135
        "ZU",  # 136
    ],
    "Monotony": [
        "DECREASING",           # 0
        "INCREASING",           # 1
        "MONOTONOUS",           # 2
        "NO-MONOTONY",          # 3
        "STRICTLY-DECREASING",  # 4
        "STRICTLY-INCREASING",  # 5
        "STRICT-MONOTONOUS",    # 6
    ],
    "PageBreak": [
        "BREAK",     # 0
        "NO-BREAK",  # 1
    ],
    "PageWide": [
        "NO-PGWIDE",  # 0
        "PGWIDE",     # 1
    ],
    "ScaleConstraintValidity": [
        "NOT-AVAILABLE",  # 0
        "NOT-DEFINED",    # 1
        "NOT-VALID",      # 2
        "VALID"           # 3
    ],
    "SwCalibrationAccess": [
        "NOT-ACCESSIBLE",  # 0
        "READ-ONLY",       # 1
        "READ-WRITE"       # 2
    ],
    "SwImplPolicy": [
        "CONST",              # 0
        "FIXED",              # 1
        "MEASUREMENT-POINT",  # 2
        "QUEUED",             # 3
        "STANDARD"            # 4
    ]
}


def enum_to_xml(enum_item: Enum, schema_version=ar_base.DEFAULT_SCHEMA_VERSION):
    """
    Converts enum value back to XML
    """
    enum_type_name = enum_item.__class__.__name__
    xml_mapping = enum_to_xml_map[enum_type_name]
    entry = xml_mapping[enum_item.value]
    if isinstance(entry, str):
        return entry
    elif isinstance(entry, VersionedTextValue):
        if schema_version not in entry.valid_versions:
            raise ar_exception.VersionError(f"'{enum_item}'")
        return entry.value
    raise NotImplementedError("Multiple entry support not yet implemented")


str_to_enum_map = {
    "PackageRole": {
        "APPLICATION_DATA_TYPE": PackageRole.APPLICATION_DATA_TYPE,
        "ApplicationDataType": PackageRole.APPLICATION_DATA_TYPE,
        "BASE_TYPE": PackageRole.BASE_TYPE,
        "BaseType": PackageRole.BASE_TYPE,
        "COMPONENT_TYPE": PackageRole.COMPONENT_TYPE,
        "ComponentType": PackageRole.COMPONENT_TYPE,
        "COMPU_METHOD": PackageRole.COMPU_METHOD,
        "CompuMethod": PackageRole.COMPU_METHOD,
        "DATA_CONSTRAINT": PackageRole.DATA_CONSTRAINT,
        "DataConstraint": PackageRole.DATA_CONSTRAINT,
        "IMPLEMENTATION_DATA_TYPE": PackageRole.IMPLEMENTATION_DATA_TYPE,
        "ImplementationDataType": PackageRole.IMPLEMENTATION_DATA_TYPE,
        "MODE_DECLARATION_GROUP": PackageRole.MODE_DECLARATION_GROUP,
        "ModeDeclartionGroup": PackageRole.MODE_DECLARATION_GROUP,
        "PORT_INTERFACE": PackageRole.PORT_INTERFACE,
        "PortInterface": PackageRole.PORT_INTERFACE,
        "Unit": PackageRole.UNIT,
        "UNIT": PackageRole.UNIT,
        "VALUE_SPECIFICATION": PackageRole.VALUE_SPECIFICATION,
        "ValueSpefication": PackageRole.VALUE_SPECIFICATION,
    }
}


def str_to_package_role(name: str) -> PackageRole:
    """
    Convert string to PackageRole Enum
    """
    return str_to_enum_map["PackageRole"][name]
