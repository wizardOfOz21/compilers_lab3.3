import parser_edsl as pe
import re

def make_keyword(image):
    return pe.Terminal(image, image, lambda name: None,
                       re_flags=re.IGNORECASE, priority=10)
    
def make_nonterminals(str):
    return map(pe.NonTerminal, str.split())

UNSIGNED_NUMBER = pe.Terminal('UNSIGNED_NUMBER', '[0-9]+', int)
IDENTIFIER = pe.Terminal('IDENTIFIER', '[A-Za-z][A-Za-z0-9]*', str.upper)

NSign, A = \
    map(pe.NonTerminal, 'Sign A'.split())
    
NSign                   |= '+', lambda: '+'
NSign                   |= '-', lambda: '-'
    
@pe.ExAction
def getFirstWithCoords(attrs, coords, res_coord):
    attr, = attrs
    cattr, = coords
    return ([attr], [cattr.start])

@pe.ExAction
def getNextWithCoords(attrs, coords, res_coord):
    list, next = attrs
    clist, ccomma, cnext = coords
    return (list[0]+[next], list[1]+[cnext.start])
