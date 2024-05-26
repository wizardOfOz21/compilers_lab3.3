from dataclasses import dataclass
import parser_edsl as pe
import typing as t
from parser.shared import UNSIGNED_NUMBER, IDENTIFIER, \
    make_keyword, make_nonterminals
from parser.constant import NConstant, Constant

@dataclass
class RecordSection:
    ident_list: list[str]
    type: 'Type'


@dataclass
class Variant:
    case_label_list: list[t.Union[float, str]]
    field_list: 'FieldList'  # forward-ref для типов 😎


@dataclass
class VariantPart:
    tag: str
    tag_type: str
    variants: list[Variant]


@dataclass
class FieldList:
    fixed_part: t.Union[None, list[RecordSection]]
    variant_part: t.Union[None, VariantPart]


KW_RECORD = make_keyword('record')
KW_NIL = make_keyword('nil')
KW_CASE = make_keyword('case')
KW_OF = make_keyword('of')
KW_END = make_keyword('end')
KW_TYPE = make_keyword('type')
KW_PACKED = make_keyword('packed')
KW_ARRAY = make_keyword('array')
KW_FILE = make_keyword('set')
KW_SET = make_keyword('file')

NTypeBlock, NTypeDefinitionList, NTypeDefinition, NType = make_nonterminals(
    'TypeBlock TypeDefinitionList TypeDefinition Type'
)

NSimpleType, NPointerType, NStructuredType, NScalarType = make_nonterminals(
    'SimpleType PointerType StructuredType ScalarType'
)
NSubrangeType, NIdentList, NUnpackedStructuredType = make_nonterminals(
    'SubrangeType IdentList UnpackedStructuredType'
)
NArrayType, NFileType, NSetType, NIndexTypeList = make_nonterminals(
    'ArrayType FileType SetType IndexTypeList'
)

NCaseLabel, NCaseLabelList = make_nonterminals(
    'CaseLabel CaseLabelList')

NVariant, NFieldList, NVariantList, NFieldIdentList = make_nonterminals(
    'Variant FieldList VariantList, FieldIdentList')

NRecordSection, NFixedPart, NVariantPart, NRecordType = make_nonterminals(
    'RecordSection FixedPart VariantPart, RecordType')

NRecordType |= KW_RECORD, NFieldList, KW_END
NFieldList |= NFixedPart, lambda v: FieldList(v, None)
NFieldList |= NFixedPart, ';', NVariantPart, FieldList
NFieldList |= NVariantPart, lambda v: FieldList(None, v)

NFixedPart |= NFixedPart, ';', NRecordSection, lambda l, v: l + [v]
NFixedPart |= NRecordSection, lambda v: [v]
NRecordSection |= NFieldIdentList, ':', NType, RecordSection
NFieldIdentList |= NFieldIdentList, ',', IDENTIFIER, lambda l, v: l + [v]
NFieldIdentList |= IDENTIFIER, lambda v: [v]

NVariantPart |= KW_CASE, IDENTIFIER, ':', IDENTIFIER, \
    KW_OF, NVariantList, VariantPart
NVariantList |= NVariantList, ';', NVariant, lambda l, v: l + [v]
NVariantList |= NVariant, lambda v: [v]

NVariant |= NCaseLabelList, ':', '(', NFieldList, ')', Variant
NCaseLabelList |= NCaseLabelList, ',', NCaseLabel, lambda l, v: l + [v]
NCaseLabelList |= NCaseLabel, lambda v: [v]
NCaseLabel |= UNSIGNED_NUMBER
NCaseLabel |= KW_NIL
NCaseLabel |= IDENTIFIER
# NCaseLabel |= STRING // TODO: добавить строки

# Тип (вынести в другой файл не получилось:
#   описание грамматики допускает циклические ссылки, а импорты пайтона нет 🙁 )


@dataclass
class FileType:
    base_type: 'Type'


@dataclass
class SetType:
    base_type: 'SimpleType'


@dataclass
class ArrayType:
    element_types: list['SimpleType']
    component_type: 'Type'


@dataclass
class RecordType:
    fields: FieldList


@dataclass
class StructuredType:
    packed: bool
    type: t.Union[ArrayType, RecordType, FileType, SetType]


@dataclass
class PointerType:
    type: str


@dataclass
class SubrangeType:
    start: Constant
    end: Constant


@dataclass
class ScalarType:
    types: list[str]


@dataclass
class SimpleType:
    val: t.Union[ScalarType, SubrangeType, str]


@dataclass
class Type:
    val: t.Union[SimpleType, PointerType, StructuredType]

@dataclass
class TypeDef:
    name: str
    type: Type

# Определение типа

NTypeBlock |= KW_TYPE, NTypeDefinitionList, ';'
NTypeDefinitionList |= NTypeDefinitionList, ';', NTypeDefinition, \
    lambda l, v: l + [v]
NTypeDefinitionList |= NTypeDefinition, lambda v: [v]
NTypeDefinition |= IDENTIFIER, '=', NType, TypeDef
NType |= NSimpleType, Type
NType |= NPointerType, Type
NType |= NStructuredType, Type
NSimpleType |= NScalarType, SimpleType
NSimpleType |= NSubrangeType, SimpleType
NSimpleType |= IDENTIFIER, SimpleType

NPointerType |= '^', IDENTIFIER, PointerType

NScalarType |= '(', NIdentList, ')', ScalarType
NIdentList |= NIdentList, ',', IDENTIFIER, lambda l, v: l + [v]
NIdentList |= IDENTIFIER, lambda v: [v]

NSubrangeType |= NConstant, '..', NConstant, SubrangeType

NStructuredType |= KW_PACKED, NUnpackedStructuredType, \
    lambda v: StructuredType(True,v)
NStructuredType |= NUnpackedStructuredType, lambda v: StructuredType(False, v)
NUnpackedStructuredType |= NArrayType
NUnpackedStructuredType |= NRecordType
NUnpackedStructuredType |= NFileType
NUnpackedStructuredType |= NSetType

NArrayType |= KW_ARRAY, '[', NIndexTypeList, ']', KW_OF, NType, ArrayType
NIndexTypeList |= NIndexTypeList, ',', NSimpleType, lambda l, v: l + [v]
NIndexTypeList |= NSimpleType, lambda v: [v]

NFileType |= KW_FILE, KW_OF, NType, FileType
NSetType |= KW_SET, KW_OF, NSimpleType, SetType


#######################
