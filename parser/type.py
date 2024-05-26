from dataclasses import dataclass
import parser_edsl as pe
import typing as t
from parser.shared import UNSIGNED_NUMBER, IDENTIFIER, \
    make_keyword, make_nonterminals
from parser.constant import NConstant, Constant
import errors as er
from parser.shared import getFirstWithCoords, getNextWithCoords


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


@dataclass
class RecordType:
    fields: FieldList

    def check(self, prog):
        pass


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

NRecordType |= KW_RECORD, NFieldList, KW_END, RecordType
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
    pos: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        type, = attrs
        cfile, cof, ctype = coords
        return FileType(type, ctype)

    def check(self, prog):
        self.base_type.check(prog)


@dataclass
class SetType:
    base_type: 'SimpleType'
    pos: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        type, = attrs
        cset, cof, ctype = coords
        return SetType(type, ctype)

    def check(self, prog):
        self.base_type.check(prog)


@dataclass
class ArrayType:
    element_types: list['SimpleType']
    component_type: 'Type'

    def check(self, prog):
        pass


@dataclass
class StructuredType:
    packed: bool
    type: t.Union[ArrayType, RecordType, FileType, SetType]

    def check(self, prog):
        self.type.check(prog)


@dataclass
class PointerType:
    type: str
    pos: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        type, = attrs
        ccaret, ctype = coords
        return PointerType(type, ctype)

    def check(self, prog):
        prog.check_defined_type_rule(self.type, self.pos)


@dataclass
class SubrangeType:
    min: Constant
    max: Constant
    points_pos: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        min, max = attrs
        cmin, cpoints, cmax = coords
        return SubrangeType(min, max, cpoints.start)

    def check(self, prog):
        min_value = self.min.check(prog)
        max_value = self.max.check(prog)

        if min_value > max_value:
            raise er.SubrangeWrongBorders(self.points_pos)


@dataclass
class ScalarType:
    types: list[str]
    names_pos: list[pe.Position]

    @pe.ExAction
    def create(attrs, coords, res_coord):
        list, = attrs
        return ScalarType(list[0], list[1])

    def check(self, prog):
        for idx, name in enumerate(self.types):
            prog.check_global_scope_rule(name, self.names_pos[idx])


@dataclass
class SimpleType:
    val: t.Union[ScalarType, SubrangeType, str]
    pos: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        attr, = attrs
        cattr, = coords
        return SimpleType(attr, cattr.start)

    def check(self, prog):
        if isinstance(self.val, str):
            prog.check_defined_type_rule(self.val, self.pos)
        else:
            self.val.check(prog)


@dataclass
class Type:
    val: t.Union[SimpleType, PointerType, StructuredType]

    def isSimple(self):
        return isinstance(
            self.val, SimpleType)

    def isScalar(self):
        return self.isSimple() and isinstance(self.val.val, ScalarType)

    def toScalar(self):
        return self.val.val

    def check(self, prog):
        self.val.check(prog)


@dataclass
class TypeDef:
    name: str
    type: Type
    name_pos: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, type = attrs
        cname, cequal, ctype = coords
        return TypeDef(name, type, cname.start)

    def check(self, prog):
        self.type.check(prog)
        prog.check_global_scope_rule(self.name, self.name_pos)
        prog.types[self.name] = self.name_pos

# Определение типа


NTypeBlock |= KW_TYPE, NTypeDefinitionList, ';'
NTypeDefinitionList |= NTypeDefinitionList, ';', NTypeDefinition, \
    lambda l, v: l + [v]
NTypeDefinitionList |= NTypeDefinition, lambda v: [v]
NTypeDefinition |= IDENTIFIER, '=', NType, TypeDef.create
NType |= NSimpleType, Type
NType |= NPointerType, Type
NType |= NStructuredType, Type
NSimpleType |= NScalarType, SimpleType.create
NSimpleType |= NSubrangeType, SimpleType.create
NSimpleType |= IDENTIFIER, SimpleType.create

NPointerType |= '^', IDENTIFIER, PointerType.create

NScalarType |= '(', NIdentList, ')', ScalarType.create
NIdentList |= NIdentList, ',', IDENTIFIER, getNextWithCoords
NIdentList |= IDENTIFIER, getFirstWithCoords

NSubrangeType |= NConstant, '..', NConstant, SubrangeType.create

NStructuredType |= KW_PACKED, NUnpackedStructuredType, \
    lambda v: StructuredType(True, v)
NStructuredType |= NUnpackedStructuredType, lambda v: StructuredType(False, v)
NUnpackedStructuredType |= NArrayType
NUnpackedStructuredType |= NRecordType
NUnpackedStructuredType |= NFileType
NUnpackedStructuredType |= NSetType

NArrayType |= KW_ARRAY, '[', NIndexTypeList, ']', KW_OF, NType, ArrayType
NIndexTypeList |= NIndexTypeList, ',', NSimpleType, lambda l, v: l + [v]
NIndexTypeList |= NSimpleType, lambda v: [v]

NFileType |= KW_FILE, KW_OF, NType, FileType.create
NSetType |= KW_SET, KW_OF, NSimpleType, SetType.create

#######################
