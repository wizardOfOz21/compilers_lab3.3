import parser_edsl as pe
import re

def make_keyword(image):
    return pe.Terminal(image, image, lambda name: None,
                       re_flags=re.IGNORECASE, priority=10)
    
def make_nonterminals(str):
    return map(pe.NonTerminal, str.split())

UNSIGNED_NUMBER = pe.Terminal('UNSIGNED_NUMBER', '[0-9]+(\\.[0-9]*)?(e[-+]?[0-9]+)?', float)
IDENTIFIER = pe.Terminal('IDENTIFIER', '[A-Za-z][A-Za-z0-9]*', str.upper)

NSign, A = \
    map(pe.NonTerminal, 'Sign A'.split())
    
NSign                   |= '+', lambda: '+'
NSign                   |= '-', lambda: '-'
    