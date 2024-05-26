from dataclasses import dataclass
import parser_edsl as pe
import typing as t
from parser.shared import NSign, UNSIGNED_NUMBER, \
    IDENTIFIER, make_keyword, make_nonterminals

@dataclass
class Constant:
    sign: t.Union[str, None]
    unsigned_constant: t.Union[str, float]
    unsigned_constant_pos: pe.Position

    @pe.ExAction
    def create_unsigned(attrs, coords, res_coord):
        value, = attrs
        cvalue, = coords
        return Constant(None, value, cvalue.start)

    @pe.ExAction
    def create(attrs, coords, res_coord):
        sign, value = attrs
        csign, cvalue = coords
        return Constant(sign, value, cvalue.start)

    def check(self, prog):
        sign_mul = +1 if self.sign != '-' else -1

        if isinstance(self.unsigned_constant, str):
            return sign_mul * prog.check_defined_constant_rule(
                self.unsigned_constant, self.unsigned_constant_pos)

        return sign_mul * self.unsigned_constant


@dataclass
class ConstDef:
    name: str
    constant: Constant
    name_pos: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, const = attrs
        cname, cequal, cconst = coords
        return ConstDef(name, const, cname.start)

    def check(self, prog):
        prog.check_global_scope_rule(self.name, self.name_pos)
        value = self.constant.check(prog)
        prog.consts[self.name] = value


NConstantBlock, NConstantDefinitionList, NConstantDefinition, NConstant = make_nonterminals(
    'ConstantBlock ConstantDefinitionList ConstantDefinition Constant')

NUnsignedConstantNumber, NUnsignedNumber = make_nonterminals(
    'UnsignedConstantNumber UnsignedNumber'
)

KW_CONST = make_keyword('const')

# Определение константы

NConstantBlock |= KW_CONST, NConstantDefinitionList, ';'
NConstantDefinitionList |= NConstantDefinitionList, ';', NConstantDefinition, \
    lambda l, v: l + [v]
NConstantDefinitionList |= NConstantDefinition, lambda v: [v]
NConstantDefinition |= IDENTIFIER, '=', NConstant, ConstDef.create
NConstant |= NSign, NUnsignedConstantNumber, Constant.create
NConstant |= NUnsignedConstantNumber, Constant.create_unsigned
NUnsignedConstantNumber |= UNSIGNED_NUMBER
NUnsignedConstantNumber |= IDENTIFIER

#######################
