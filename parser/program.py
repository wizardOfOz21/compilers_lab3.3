import parser_edsl as pe
from dataclasses import dataclass
import typing as t
from parser.constant import NConstantBlock, ConstDef
from parser.type import NTypeBlock, TypeDef

@dataclass
class Program:
    defs : list[t.Union[TypeDef, ConstDef]]

NProgram, NBlocks, NBlock = \
    map(pe.NonTerminal, 'Program Blocks Block'.split())

NProgram  |= NBlocks, Program
NBlocks   |= NBlocks, NBlock, lambda l, v: l + v 
NBlocks   |= NBlock, lambda v: v
NBlock    |= NTypeBlock
NBlock    |= NConstantBlock
