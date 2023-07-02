"""
Enum Definitions
"""

from enum import Enum

# from typing import Any
from dataclasses import dataclass
import autosar.xml.exception as ar_exception

DEFAULT_SCHEMA_VERSION = 50


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


class IdentifiableSubTypes(Enum):
    """
    IDENTIFIABLE--SUBTYPES-ENUM

    This is just a small subset.
    More items will be added as implementation progresses.
    """

    APPLICATION_ARRAY_DATA_TYPE = 0
    APPLICATION_ASSOC_MAP_DATA_TYPE = 1
    APPLICATION_COMPOSITE_DATA_TYPE = 2
    APPLICATION_DATA_TYPE = 3
    APPLICATION_DEFERRED_DATA_TYPE = 4
    APPLICATION_PRIMITIVE_DATA_TYPE = 5
    APPLICATION_RECORD_DATA_TYPE = 6
    BSW_MODULE_ENTRY = 7
    COMPU_METHOD = 8
    DATA_CONSTR = 9
    IMPLEMENTATION_DATA_TYPE = 10
    UNIT = 11
    PHYSICAL_DIMENSION = 12
    SW_ADDR_METHOD = 13
    SW_BASE_TYPE = 14


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
    FLOAT = 2
    HEXADECIMAL = 3
    BINARY = 4
    SCIENTIFIC = 5


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
        "PAYLOAD-AS-ARRAY": VersionedEnumValue(ArrayImplPolicy.PAYLOAD_AS_ARRAY, {50}),
        "PAYLOAD-AS-POINTER-TO-ARRAY": VersionedEnumValue(ArrayImplPolicy.PAYLOAD_AS_POINTER_TO_ARRAY, {50}),
    },
    "ArraySizeHandling": {
        "ALL-INDICES-DIFFERENT-ARRAY-SIZE": ArraySizeHandling.ALL_INDICES_DIFFERENT_ARRAY_SIZE,
        "ALL-INDICES-SAME-ARRAY-SIZE": ArraySizeHandling.ALL_INDICES_SAME_ARRAY_SIZE,
        "INHERITED-FROM-ARRAY-ELEMENT-TYPE-SIZE": ArraySizeHandling.INHERITED_FROM_ARRAY_ELEMENT_TYPE_SIZE
    },
    "ArraySizeSemantics": {
        "FIXED-SIZE": VersionedEnumValue(ArraySizeSemantics.FIXED_SIZE, {50}),
        "VARIABLE-SIZE": VersionedEnumValue(ArraySizeSemantics.VARIABLE_SIZE, {50}),
    },
    "ByteOrder": {
        "MOST-SIGNIFICANT-BYTE-FIRST": VersionedEnumValue(ByteOrder.BIG_ENDIAN, {50}),
        "MOST-SIGNIFICANT-BYTE-LAST": VersionedEnumValue(ByteOrder.LITTLE_ENDIAN, {50}),
        "OPAQUE": VersionedEnumValue(ByteOrder.OPAQUE, {50}),
    },
    "DisplayPresentation": {
        "PRESENTATION-CONTINUOUS": VersionedEnumValue(DisplayPresentation.CONTINUOUS, {50}),
        "PRESENTATION-DISCRETE": VersionedEnumValue(DisplayPresentation.DISCRETE, {50}),
    },
    "EmphasisFont": {
        "DEFAULT": VersionedEnumValue(EmphasisFont.DEFAULT, {50}),
        "MONO": VersionedEnumValue(EmphasisFont.MONO, {50}),
    },
    "EmphasisType": {
        "BOLD": VersionedEnumValue(EmphasisType.BOLD, {50}),
        "BOLDITALIC": VersionedEnumValue(EmphasisType.BOLDITALIC, {50}),
        "ITALIC": VersionedEnumValue(EmphasisType.ITALIC, {50}),
        "PLAIN": VersionedEnumValue(EmphasisType.PLAIN, {50}),
    },
    "Float": {
        "FLOAT": VersionedEnumValue(Float.FLOAT, {50}),
        "NO-FLOAT": VersionedEnumValue(Float.NO_FLOAT, {50}),
    },
    "IdentifiableSubTypes": {
        "APPLICATION-ARRAY-DATA-TYPE": IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE,
        "APPLICATION-ASSOC-MAP-DATA-TYPE": IdentifiableSubTypes.APPLICATION_ASSOC_MAP_DATA_TYPE,
        "APPLICATION-COMPOSITE-DATA-TYPE": IdentifiableSubTypes.APPLICATION_COMPOSITE_DATA_TYPE,
        "APPLICATION-DATA-TYPE": IdentifiableSubTypes.APPLICATION_DATA_TYPE,
        "APPLICATION-DEFERRED-DATA-TYPE": IdentifiableSubTypes.APPLICATION_DEFERRED_DATA_TYPE,
        "APPLICATION-PRIMITIVE-DATA-TYPE": IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE,
        "APPLICATION-RECORD-DATA-TYPE": IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE,
        "BSW-MODULE-ENTRY": IdentifiableSubTypes.BSW_MODULE_ENTRY,
        "COMPU-METHOD": IdentifiableSubTypes.COMPU_METHOD,
        "DATA-CONSTR": IdentifiableSubTypes.DATA_CONSTR,
        "IMPLEMENTATION-DATA-TYPE": IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE,
        "UNIT": IdentifiableSubTypes.UNIT,
        "PHYSICAL-DIMENSION": IdentifiableSubTypes.PHYSICAL_DIMENSION,
        "SW-ADDR-METHOD": IdentifiableSubTypes.SW_ADDR_METHOD,
        "SW-BASE-TYPE": IdentifiableSubTypes.SW_BASE_TYPE,
    },
    "IntervalType": {
        "CLOSED": IntervalType.CLOSED,
        "OPEN": IntervalType.OPEN
    },
    "KeepWithPrevious": {
        "KEEP": VersionedEnumValue(KeepWithPrevious.KEEP, {50}),
        "NO-KEEP": VersionedEnumValue(KeepWithPrevious.NO_KEEP, {50}),
    },
    "Language": {
        "AA": VersionedEnumValue(Language.AA, {50}),
        "AB": VersionedEnumValue(Language.AB, {50}),
        "AF": VersionedEnumValue(Language.AF, {50}),
        "AM": VersionedEnumValue(Language.AM, {50}),
        "AR": VersionedEnumValue(Language.AR, {50}),
        "AS": VersionedEnumValue(Language.AS, {50}),
        "AY": VersionedEnumValue(Language.AY, {50}),
        "AZ": VersionedEnumValue(Language.AZ, {50}),
        "BA": VersionedEnumValue(Language.BA, {50}),
        "BE": VersionedEnumValue(Language.BE, {50}),
        "BG": VersionedEnumValue(Language.BG, {50}),
        "BH": VersionedEnumValue(Language.BH, {50}),
        "BI": VersionedEnumValue(Language.BI, {50}),
        "BN": VersionedEnumValue(Language.BN, {50}),
        "BO": VersionedEnumValue(Language.BO, {50}),
        "BR": VersionedEnumValue(Language.BR, {50}),
        "CA": VersionedEnumValue(Language.CA, {50}),
        "CO": VersionedEnumValue(Language.CO, {50}),
        "CS": VersionedEnumValue(Language.CS, {50}),
        "CY": VersionedEnumValue(Language.CY, {50}),
        "DA": VersionedEnumValue(Language.DA, {50}),
        "DE": VersionedEnumValue(Language.DE, {50}),
        "DZ": VersionedEnumValue(Language.DZ, {50}),
        "EL": VersionedEnumValue(Language.EL, {50}),
        "EN": VersionedEnumValue(Language.EN, {50}),
        "EO": VersionedEnumValue(Language.EO, {50}),
        "ES": VersionedEnumValue(Language.ES, {50}),
        "ET": VersionedEnumValue(Language.ET, {50}),
        "EU": VersionedEnumValue(Language.EU, {50}),
        "FA": VersionedEnumValue(Language.FA, {50}),
        "FI": VersionedEnumValue(Language.FI, {50}),
        "FJ": VersionedEnumValue(Language.FJ, {50}),
        "FO": VersionedEnumValue(Language.FO, {50}),
        "FOR-ALL": VersionedEnumValue(Language.FOR_ALL, {50}),
        "FR": VersionedEnumValue(Language.FR, {50}),
        "FY": VersionedEnumValue(Language.FY, {50}),
        "GA": VersionedEnumValue(Language.GA, {50}),
        "GD": VersionedEnumValue(Language.GD, {50}),
        "GL": VersionedEnumValue(Language.GL, {50}),
        "GN": VersionedEnumValue(Language.GN, {50}),
        "GU": VersionedEnumValue(Language.GU, {50}),
        "HA": VersionedEnumValue(Language.HA, {50}),
        "HI": VersionedEnumValue(Language.HI, {50}),
        "HR": VersionedEnumValue(Language.HR, {50}),
        "HU": VersionedEnumValue(Language.HU, {50}),
        "HY": VersionedEnumValue(Language.HY, {50}),
        "IA": VersionedEnumValue(Language.IA, {50}),
        "IE": VersionedEnumValue(Language.IE, {50}),
        "IK": VersionedEnumValue(Language.IK, {50}),
        "IN": VersionedEnumValue(Language.IN, {50}),
        "IS": VersionedEnumValue(Language.IS, {50}),
        "IT": VersionedEnumValue(Language.IT, {50}),
        "IW": VersionedEnumValue(Language.IW, {50}),
        "JA": VersionedEnumValue(Language.JA, {50}),
        "JI": VersionedEnumValue(Language.JI, {50}),
        "JW": VersionedEnumValue(Language.JW, {50}),
        "KA": VersionedEnumValue(Language.KA, {50}),
        "KK": VersionedEnumValue(Language.KK, {50}),
        "KL": VersionedEnumValue(Language.KL, {50}),
        "KM": VersionedEnumValue(Language.KM, {50}),
        "KN": VersionedEnumValue(Language.KN, {50}),
        "KO": VersionedEnumValue(Language.KO, {50}),
        "KS": VersionedEnumValue(Language.KS, {50}),
        "KU": VersionedEnumValue(Language.KU, {50}),
        "KY": VersionedEnumValue(Language.KY, {50}),
        "LA": VersionedEnumValue(Language.LA, {50}),
        "LN": VersionedEnumValue(Language.LN, {50}),
        "LO": VersionedEnumValue(Language.LO, {50}),
        "LT": VersionedEnumValue(Language.LT, {50}),
        "LV": VersionedEnumValue(Language.LV, {50}),
        "MG": VersionedEnumValue(Language.MG, {50}),
        "MI": VersionedEnumValue(Language.MI, {50}),
        "MK": VersionedEnumValue(Language.MK, {50}),
        "ML": VersionedEnumValue(Language.ML, {50}),
        "MN": VersionedEnumValue(Language.MN, {50}),
        "MO": VersionedEnumValue(Language.MO, {50}),
        "MR": VersionedEnumValue(Language.MR, {50}),
        "MS": VersionedEnumValue(Language.MS, {50}),
        "MT": VersionedEnumValue(Language.MT, {50}),
        "MY": VersionedEnumValue(Language.MY, {50}),
        "NA": VersionedEnumValue(Language.NA, {50}),
        "NE": VersionedEnumValue(Language.NE, {50}),
        "NL": VersionedEnumValue(Language.NL, {50}),
        "NO": VersionedEnumValue(Language.NO, {50}),
        "OC": VersionedEnumValue(Language.OC, {50}),
        "OM": VersionedEnumValue(Language.OM, {50}),
        "OR": VersionedEnumValue(Language.OR, {50}),
        "PA": VersionedEnumValue(Language.PA, {50}),
        "PL": VersionedEnumValue(Language.PL, {50}),
        "PS": VersionedEnumValue(Language.PS, {50}),
        "PT": VersionedEnumValue(Language.PT, {50}),
        "QU": VersionedEnumValue(Language.QU, {50}),
        "RM": VersionedEnumValue(Language.RM, {50}),
        "RN": VersionedEnumValue(Language.RN, {50}),
        "RO": VersionedEnumValue(Language.RO, {50}),
        "RU": VersionedEnumValue(Language.RU, {50}),
        "RW": VersionedEnumValue(Language.RW, {50}),
        "SA": VersionedEnumValue(Language.SA, {50}),
        "SD": VersionedEnumValue(Language.SD, {50}),
        "SG": VersionedEnumValue(Language.SG, {50}),
        "SH": VersionedEnumValue(Language.SH, {50}),
        "SI": VersionedEnumValue(Language.SI, {50}),
        "SK": VersionedEnumValue(Language.SK, {50}),
        "SL": VersionedEnumValue(Language.SL, {50}),
        "SM": VersionedEnumValue(Language.SM, {50}),
        "SN": VersionedEnumValue(Language.SN, {50}),
        "SO": VersionedEnumValue(Language.SO, {50}),
        "SQ": VersionedEnumValue(Language.SQ, {50}),
        "SR": VersionedEnumValue(Language.SR, {50}),
        "SS": VersionedEnumValue(Language.SS, {50}),
        "ST": VersionedEnumValue(Language.ST, {50}),
        "SU": VersionedEnumValue(Language.SU, {50}),
        "SV": VersionedEnumValue(Language.SV, {50}),
        "SW": VersionedEnumValue(Language.SW, {50}),
        "TA": VersionedEnumValue(Language.TA, {50}),
        "TE": VersionedEnumValue(Language.TE, {50}),
        "TG": VersionedEnumValue(Language.TG, {50}),
        "TH": VersionedEnumValue(Language.TH, {50}),
        "TI": VersionedEnumValue(Language.TI, {50}),
        "TK": VersionedEnumValue(Language.TK, {50}),
        "TL": VersionedEnumValue(Language.TL, {50}),
        "TN": VersionedEnumValue(Language.TN, {50}),
        "TO": VersionedEnumValue(Language.TO, {50}),
        "TR": VersionedEnumValue(Language.TR, {50}),
        "TS": VersionedEnumValue(Language.TS, {50}),
        "TT": VersionedEnumValue(Language.TT, {50}),
        "TW": VersionedEnumValue(Language.TW, {50}),
        "UK": VersionedEnumValue(Language.UK, {50}),
        "UR": VersionedEnumValue(Language.UR, {50}),
        "UZ": VersionedEnumValue(Language.UZ, {50}),
        "VI": VersionedEnumValue(Language.VI, {50}),
        "VO": VersionedEnumValue(Language.VO, {50}),
        "WO": VersionedEnumValue(Language.WO, {50}),
        "XH": VersionedEnumValue(Language.XH, {50}),
        "YO": VersionedEnumValue(Language.YO, {50}),
        "ZH": VersionedEnumValue(Language.ZH, {50}),
        "ZU": VersionedEnumValue(Language.ZU, {50}),
    },
    "Monotony": {
        "DECREASING": VersionedEnumValue(Monotony.DECREASING, {50}),
        "INCREASING": VersionedEnumValue(Monotony.INCREASING, {50}),
        "MONOTONOUS": VersionedEnumValue(Monotony.MONOTONOUS, {50}),
        "NO-MONOTONY": VersionedEnumValue(Monotony.NO_MONOTONY, {50}),
        "STRICTLY-DECREASING": VersionedEnumValue(Monotony.STRICTLY_DECREASING, {50}),
        "STRICTLY-INCREASING": VersionedEnumValue(Monotony.STRICTLY_INCREASING, {50}),
        "STRICT-MONOTONOUS": VersionedEnumValue(Monotony.STRICT_MONOTONOUS, {50}),
    },
    "PageBreak": {
        "BREAK": VersionedEnumValue(PageBreak.BREAK, {50}),
        "NO-BREAK": VersionedEnumValue(PageBreak.NO_BREAK, {50}),
    },
    "PageWide": {
        "NO-PGWIDE": VersionedEnumValue(PageWide.NO_PGWIDE, {50}),
        "PGWIDE": VersionedEnumValue(PageWide.PGWIDE, {50}),
    },
    "ScaleConstraintValidity": {
        "NOT-AVAILABLE": ScaleConstraintValidity.NOT_AVAILABLE,
        "NOT-DEFINED": ScaleConstraintValidity.NOT_DEFINED,
        "NOT-VALID": ScaleConstraintValidity.NOT_VALID,
        "VALID": ScaleConstraintValidity.VALID
    },
    "SwCalibrationAccess": {
        "NOT-ACCESSIBLE": VersionedEnumValue(SwCalibrationAccess.NOT_ACCESSIBLE, {50}),
        "READ-ONLY": VersionedEnumValue(SwCalibrationAccess.READ_ONLY, {50}),
        "READ-WRITE": VersionedEnumValue(SwCalibrationAccess.READ_WRITE, {50}),
    },
    "SwImplPolicy": {
        "CONST": SwImplPolicy.CONST,
        "FIXED": SwImplPolicy.FIXED,
        "MEASUREMENT-POINT": SwImplPolicy.MEASUREMENT_POINT,
        "QUEUED": SwImplPolicy.QUEUED,
        "STANDARD": SwImplPolicy.STANDARD
    }
}


def xml_to_enum(enum_type_name: str, xml_text: str, schema_version: int = DEFAULT_SCHEMA_VERSION) -> Enum:
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
        VersionedTextValue("PAYLOAD-AS-ARRAY", {50}),             # 0
        VersionedTextValue("PAYLOAD-AS-POINTER-TO-ARRAY", {50}),  # 1
    ],
    "ArraySizeHandling": [
        "ALL-INDICES-DIFFERENT-ARRAY-SIZE",       # 0
        "ALL-INDICES-SAME-ARRAY-SIZE",            # 1
        "INHERITED-FROM-ARRAY-ELEMENT-TYPE-SIZE"  # 2
    ],
    "ArraySizeSemantics": [
        VersionedTextValue("FIXED-SIZE", {50}),     # 0
        VersionedTextValue("VARIABLE-SIZE", {50}),  # 1
    ],
    "ByteOrder": [
        VersionedTextValue("MOST-SIGNIFICANT-BYTE-FIRST", {50}),  # 0
        VersionedTextValue("MOST-SIGNIFICANT-BYTE-LAST", {50}),   # 1
        VersionedTextValue("OPAQUE", {50}),                       # 2
    ],
    "DisplayPresentation": [
        VersionedTextValue("PRESENTATION-CONTINUOUS", {50}),  # 0
        VersionedTextValue("PRESENTATION-DISCRETE", {50}),  # 1
    ],
    "EmphasisFont": [
        VersionedTextValue("DEFAULT", {50}),  # 0
        VersionedTextValue("MONO", {50}),  # 1
    ],
    "EmphasisType": [
        VersionedTextValue("BOLD", {50}),  # 0
        VersionedTextValue("BOLDITALIC", {50}),  # 1
        VersionedTextValue("ITALIC", {50}),  # 2
        VersionedTextValue("PLAIN", {50}),  # 3
    ],
    "Float": [
        VersionedTextValue("FLOAT", {50}),  # 0
        VersionedTextValue("NO-FLOAT", {50}),  # 1
    ],
    "IdentifiableSubTypes": [
        "APPLICATION-ARRAY-DATA-TYPE",      # 0
        "APPLICATION-ASSOC-MAP-DATA-TYPE",  # 1
        "APPLICATION-COMPOSITE-DATA-TYPE",  # 2
        "APPLICATION-DATA-TYPE",            # 3
        "APPLICATION-DEFERRED-DATA-TYPE",   # 4
        "APPLICATION_PRIMITIVE_DATA_TYPE",  # 5
        "APPLICATION-RECORD-DATA-TYPE",     # 6
        "BSW-MODULE-ENTRY",                 # 7
        "COMPU-METHOD",                     # 8
        "DATA-CONSTR",                      # 9
        "IMPLEMENTATION-DATA-TYPE",         # 10
        "UNIT",                             # 11
        "PHYSICAL-DIMENSION",               # 12
        "SW-ADDR-METHOD",                   # 13
        "SW-BASE-TYPE",                     # 14
    ],
    "IntervalType": [
        "CLOSED",  # 0
        "OPEN"  # 1
    ],
    "KeepWithPrevious": [
        VersionedTextValue("KEEP", {50}),  # 0
        VersionedTextValue("NO-KEEP", {50}),  # 1
    ],
    "Language": [
        VersionedTextValue("AA", {50}),  # 0
        VersionedTextValue("AB", {50}),  # 1
        VersionedTextValue("AF", {50}),  # 2
        VersionedTextValue("AM", {50}),  # 3
        VersionedTextValue("AR", {50}),  # 4
        VersionedTextValue("AS", {50}),  # 5
        VersionedTextValue("AY", {50}),  # 6
        VersionedTextValue("AZ", {50}),  # 7
        VersionedTextValue("BA", {50}),  # 8
        VersionedTextValue("BE", {50}),  # 9
        VersionedTextValue("BG", {50}),  # 10
        VersionedTextValue("BH", {50}),  # 11
        VersionedTextValue("BI", {50}),  # 12
        VersionedTextValue("BN", {50}),  # 13
        VersionedTextValue("BO", {50}),  # 14
        VersionedTextValue("BR", {50}),  # 15
        VersionedTextValue("CA", {50}),  # 16
        VersionedTextValue("CO", {50}),  # 17
        VersionedTextValue("CS", {50}),  # 18
        VersionedTextValue("CY", {50}),  # 19
        VersionedTextValue("DA", {50}),  # 20
        VersionedTextValue("DE", {50}),  # 21
        VersionedTextValue("DZ", {50}),  # 22
        VersionedTextValue("EL", {50}),  # 23
        VersionedTextValue("EN", {50}),  # 24
        VersionedTextValue("EO", {50}),  # 25
        VersionedTextValue("ES", {50}),  # 26
        VersionedTextValue("ET", {50}),  # 27
        VersionedTextValue("EU", {50}),  # 28
        VersionedTextValue("FA", {50}),  # 29
        VersionedTextValue("FI", {50}),  # 30
        VersionedTextValue("FJ", {50}),  # 31
        VersionedTextValue("FO", {50}),  # 32
        VersionedTextValue("FOR-ALL", {50}),  # 33
        VersionedTextValue("FR", {50}),  # 34
        VersionedTextValue("FY", {50}),  # 35
        VersionedTextValue("GA", {50}),  # 36
        VersionedTextValue("GD", {50}),  # 37
        VersionedTextValue("GL", {50}),  # 38
        VersionedTextValue("GN", {50}),  # 39
        VersionedTextValue("GU", {50}),  # 40
        VersionedTextValue("HA", {50}),  # 41
        VersionedTextValue("HI", {50}),  # 42
        VersionedTextValue("HR", {50}),  # 43
        VersionedTextValue("HU", {50}),  # 44
        VersionedTextValue("HY", {50}),  # 45
        VersionedTextValue("IA", {50}),  # 46
        VersionedTextValue("IE", {50}),  # 47
        VersionedTextValue("IK", {50}),  # 48
        VersionedTextValue("IN", {50}),  # 49
        VersionedTextValue("IS", {50}),  # 50
        VersionedTextValue("IT", {50}),  # 51
        VersionedTextValue("IW", {50}),  # 52
        VersionedTextValue("JA", {50}),  # 53
        VersionedTextValue("JI", {50}),  # 54
        VersionedTextValue("JW", {50}),  # 55
        VersionedTextValue("KA", {50}),  # 56
        VersionedTextValue("KK", {50}),  # 57
        VersionedTextValue("KL", {50}),  # 58
        VersionedTextValue("KM", {50}),  # 59
        VersionedTextValue("KN", {50}),  # 60
        VersionedTextValue("KO", {50}),  # 61
        VersionedTextValue("KS", {50}),  # 62
        VersionedTextValue("KU", {50}),  # 63
        VersionedTextValue("KY", {50}),  # 64
        VersionedTextValue("LA", {50}),  # 65
        VersionedTextValue("LN", {50}),  # 66
        VersionedTextValue("LO", {50}),  # 67
        VersionedTextValue("LT", {50}),  # 68
        VersionedTextValue("LV", {50}),  # 69
        VersionedTextValue("MG", {50}),  # 70
        VersionedTextValue("MI", {50}),  # 71
        VersionedTextValue("MK", {50}),  # 72
        VersionedTextValue("ML", {50}),  # 73
        VersionedTextValue("MN", {50}),  # 74
        VersionedTextValue("MO", {50}),  # 75
        VersionedTextValue("MR", {50}),  # 76
        VersionedTextValue("MS", {50}),  # 77
        VersionedTextValue("MT", {50}),  # 78
        VersionedTextValue("MY", {50}),  # 79
        VersionedTextValue("NA", {50}),  # 80
        VersionedTextValue("NE", {50}),  # 81
        VersionedTextValue("NL", {50}),  # 82
        VersionedTextValue("NO", {50}),  # 83
        VersionedTextValue("OC", {50}),  # 84
        VersionedTextValue("OM", {50}),  # 85
        VersionedTextValue("OR", {50}),  # 86
        VersionedTextValue("PA", {50}),  # 87
        VersionedTextValue("PL", {50}),  # 88
        VersionedTextValue("PS", {50}),  # 89
        VersionedTextValue("PT", {50}),  # 90
        VersionedTextValue("QU", {50}),  # 91
        VersionedTextValue("RM", {50}),  # 92
        VersionedTextValue("RN", {50}),  # 93
        VersionedTextValue("RO", {50}),  # 94
        VersionedTextValue("RU", {50}),  # 95
        VersionedTextValue("RW", {50}),  # 96
        VersionedTextValue("SA", {50}),  # 97
        VersionedTextValue("SD", {50}),  # 98
        VersionedTextValue("SG", {50}),  # 99
        VersionedTextValue("SH", {50}),  # 100
        VersionedTextValue("SI", {50}),  # 101
        VersionedTextValue("SK", {50}),  # 102
        VersionedTextValue("SL", {50}),  # 103
        VersionedTextValue("SM", {50}),  # 104
        VersionedTextValue("SN", {50}),  # 105
        VersionedTextValue("SO", {50}),  # 106
        VersionedTextValue("SQ", {50}),  # 107
        VersionedTextValue("SR", {50}),  # 108
        VersionedTextValue("SS", {50}),  # 109
        VersionedTextValue("ST", {50}),  # 110
        VersionedTextValue("SU", {50}),  # 111
        VersionedTextValue("SV", {50}),  # 112
        VersionedTextValue("SW", {50}),  # 113
        VersionedTextValue("TA", {50}),  # 114
        VersionedTextValue("TE", {50}),  # 115
        VersionedTextValue("TG", {50}),  # 116
        VersionedTextValue("TH", {50}),  # 117
        VersionedTextValue("TI", {50}),  # 118
        VersionedTextValue("TK", {50}),  # 119
        VersionedTextValue("TL", {50}),  # 120
        VersionedTextValue("TN", {50}),  # 121
        VersionedTextValue("TO", {50}),  # 122
        VersionedTextValue("TR", {50}),  # 123
        VersionedTextValue("TS", {50}),  # 124
        VersionedTextValue("TT", {50}),  # 125
        VersionedTextValue("TW", {50}),  # 126
        VersionedTextValue("UK", {50}),  # 127
        VersionedTextValue("UR", {50}),  # 128
        VersionedTextValue("UZ", {50}),  # 129
        VersionedTextValue("VI", {50}),  # 130
        VersionedTextValue("VO", {50}),  # 131
        VersionedTextValue("WO", {50}),  # 132
        VersionedTextValue("XH", {50}),  # 133
        VersionedTextValue("YO", {50}),  # 134
        VersionedTextValue("ZH", {50}),  # 135
        VersionedTextValue("ZU", {50}),  # 136
    ],
    "Monotony": [
        VersionedTextValue("DECREASING", {50}),           # 0
        VersionedTextValue("INCREASING", {50}),           # 1
        VersionedTextValue("MONOTONOUS", {50}),           # 2
        VersionedTextValue("NO-MONOTONY", {50}),          # 3
        VersionedTextValue("STRICTLY-DECREASING", {50}),  # 4
        VersionedTextValue("STRICTLY-INCREASING", {50}),  # 5
        VersionedTextValue("STRICT-MONOTONOUS", {50}),    # 6
    ],
    "PageBreak": [
        VersionedTextValue("BREAK", {50}),  # 0
        VersionedTextValue("NO-BREAK", {50}),  # 1
    ],
    "PageWide": [
        VersionedTextValue("NO-PGWIDE", {50}),  # 0
        VersionedTextValue("PGWIDE", {50}),  # 1
    ],
    "ScaleConstraintValidity": [
        "NOT-AVAILABLE",   # 0
        "NOT-DEFINED",     # 1
        "NOT-VALID",       # 2
        "VALID"            # 3
    ],
    "SwCalibrationAccess": [
        "NOT-ACCESSIBLE",    # 0
        "READ-ONLY",         # 1
        "READ-WRITE"         # 2
    ],
    "SwImplPolicy": [
        "CONST",                # 0
        "FIXED",                # 1
        "MEASUREMENT-POINT",    # 2
        "QUEUED",               # 3
        "STANDARD"              # 4
    ]
}


def enum_to_xml(enum_item: Enum, schema_version=DEFAULT_SCHEMA_VERSION):
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
