import parser_edsl as pe
from dataclasses import dataclass
import typing as t
from parser.constant import NConstantBlock
from parser.type import TypeDef
from parser.constant import ConstDef

@dataclass
class Program:
    const_defs : list[ConstDef]
    type_defs : list[TypeDef]

def aggregateProgram(program, defs):
    assert len(defs) != 0
    if isinstance(defs[0], ConstDef):
        program.const_defs.extend(defs)
    elif isinstance(defs[0], TypeDef):
        program.type_defs.extend(defs)
    return program

def createProgram(defs: list[t.Union[ConstDef, TypeDef]]):
    assert len(defs) != 0
    if isinstance(defs[0], ConstDef):
       return Program(defs,[])
    elif isinstance(defs[0], TypeDef):
        return Program([],defs)

NProgram, NBlocks, NBlock = \
    map(pe.NonTerminal, 'Program Blocks Block'.split())

NProgram  |= NBlocks
NBlocks   |= NBlocks, NBlock, aggregateProgram
NBlocks   |= NBlock, createProgram
# NBlock  |= NTypeBlock
NBlock    |= NConstantBlock