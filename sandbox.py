import parser_edsl as pe
import re

def make_keyword(image):
    return pe.Terminal(image, image, lambda name: None,
                       re_flags=re.IGNORECASE, priority=10)

def make_keywords(str):
    return map(make_keyword, str.split())
    
KW_CONST, = make_keywords('const')
