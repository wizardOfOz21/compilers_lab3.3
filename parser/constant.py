from dataclasses import dataclass
import parser_edsl as pe
import typing as t
from parser.shared import NSign, UNSIGNED_NUMBER, \
    IDENTIFIER, make_keyword, make_nonterminals

@dataclass
class Constant:
    sign: t.Union[str, None]
    unsigned_constant: t.Union[str, float]

@dataclass
class ConstDef:
    name: str
    contant: Constant


NConstantBlock, NConstantDefinitionList, NConstantDefinition, NConstant = make_nonterminals(
    'ConstantBlock ConstantDefinitionList ConstantDefinition Constant'
)

NUnsignedConstantNumber, NUnsignedNumber = make_nonterminals(
    'UnsignedConstantNumber UnsignedNumber'
)

KW_CONST = make_keyword('const')

# Определение константы

NConstantBlock |= KW_CONST, NConstantDefinitionList, ';'
NConstantDefinitionList |= NConstantDefinitionList, ';', NConstantDefinition, \
    lambda l, v: l + [v]
NConstantDefinitionList |= NConstantDefinition, lambda v: [v]
NConstantDefinition |= IDENTIFIER, '=', NConstant, ConstDef
NConstant |= NSign, NUnsignedConstantNumber, Constant
NConstant |= NUnsignedConstantNumber, lambda v: Constant(None, v)
NUnsignedConstantNumber |= UNSIGNED_NUMBER
NUnsignedConstantNumber |= IDENTIFIER

#######################
