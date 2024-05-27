from enum import Enum
from dataclasses import dataclass
import parser_edsl as pe
import errors as er
import typing as t
from parser.shared import NSign, INT, REAL, STRING, \
    IDENTIFIER, make_keyword, make_nonterminals
@dataclass
class Ref:
    val: str
    pos: pe.Position
    
    @pe.ExAction
    def create(attrs, coords, res_coord):
        val, = attrs
        cval, = coords
        return Ref(val, cval)

    def check(self, prog):
        return prog.check_defined_constant_rule(self.val, self.pos)

@dataclass
class RefConstant:
    sign: t.Literal[1, -1, None]
    ref: 'Ref'

    sign_pos: pe.Position

    def check(self, prog):
        ref_val = self.ref.check(prog)
        if isinstance(ref_val, str):
            if self.sign != None:
                raise er.SignedString(self.sign_pos, self.ref.val)
            return self.ref.check(prog)
        
        return (-1 if self.sign == '-' else 1) * self.ref.check(prog)

@dataclass
class Constant:
    val: t.Union[float, int, str, RefConstant]
    
    @pe.ExAction
    def create_signed(attrs, coords, res_coord):
        sign, arg = attrs
        csign, carg = coords
        if sign != None:
            sign = -1 if sign == '-' else 1

        if isinstance(arg, Ref):
            return  Constant(RefConstant(sign, arg, csign))
        
        return Constant((-1 if sign == '-' else 1) * arg)
    
    def create_unsigned(arg):
        if isinstance(arg, Ref):
            return Constant(RefConstant(None, arg, None))
        
        return Constant(arg)
    
    def check(self, prog):
        if isinstance(self.val, RefConstant):
            return self.val.check(prog)
        return self.val
    

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

NConstant |= NSign, NUnsignedConstantNumber, Constant.create_signed
NConstant |= NUnsignedConstantNumber, Constant.create_unsigned
NConstant |= STRING, Constant
NUnsignedConstantNumber |= REAL
NUnsignedConstantNumber |= INT
NUnsignedConstantNumber |= IDENTIFIER, Ref.create

#######################
