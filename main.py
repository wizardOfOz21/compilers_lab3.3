import parser_edsl as pe
import sys
from pprint import pprint
from parser.program import NProgram

p = pe.Parser(NProgram)
assert p.is_lalr_one()

p.add_skipped_domain('\\s')
p.add_skipped_domain('(\\(\\*|\\{).*?(\\*\\)|\\})')

for filename in sys.argv[1:]:
    try:
        with open(filename) as f:
            tree = p.parse(f.read())
            # pprint(tree)
            tree.check()
            tree.print_consts()
            print('Программа корректна')
            
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')
