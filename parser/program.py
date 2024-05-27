import parser_edsl as pe
from dataclasses import dataclass
import typing as t
from parser.constant import NConstantBlock, ConstDef
from parser.type import NTypeBlock, TypeDef
import errors as er

@dataclass
class Program:
    defs: list[t.Union[TypeDef, ConstDef]]

    names = {}
    consts = {}
    types = {}
    
    def check_defined_constant_rule(self, constname, pos):
        if constname in self.consts:
            return self.consts[constname]
        raise er.UnknownConstant(pos, constname)
    
    def check_defined_type_rule(self, typename, pos):
        if typename in self.types:
            return
        raise er.UnknownType(pos, typename)
        
    def check_global_scope_rule(self, name, pos):
        if name in self.names:
            prev_def_pos = self.names[name]
            raise er.RepeatedVariable(pos, name, prev_def_pos)
        else:
            self.names[name] = pos
            
    def print_consts(self):
        print('Consts:')
        for const in self.consts:
            print(f'{const} = {self.consts[const]};')
        print('Types:')
        for type in self.types:
            print(f'{type} = {self.types[type]};')

    def check(self):
        for _def in self.defs:
            _def.check(self)

NProgram, NBlocks, NBlock = \
    map(pe.NonTerminal, 'Program Blocks Block'.split())

NProgram |= NBlocks, Program
NBlocks |= NBlocks, NBlock, lambda l, v: l + v
NBlocks |= NBlock, lambda v: v
NBlock |= NTypeBlock
NBlock |= NConstantBlock
