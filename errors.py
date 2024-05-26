import parser_edsl as pe

class SemanticError(pe.Error):
    pass

class SubrangeWrongBorders(SemanticError):
    def __init__(self, pos):
        self.pos = pos
        self.min = min
        self.max = max

    @property
    def message(self):
        return f'Левая граница диапазона превышает правую'

class RepeatedVariable(SemanticError):
    def __init__(self, pos, varname, prev_def_pos):
        self.pos = pos
        self.varname = varname
        self.prev_def = prev_def_pos

    @property
    def message(self):
        return f'Имя \'{self.varname}\' уже было объявлено ранее: {self.prev_def}'

class UnknownType(SemanticError):
    def __init__(self, pos, typename):
        self.pos = pos
        self.typename = typename

    @property
    def message(self):
        return f'Тип \'{self.typename}\' ранее не был объявлен'

class UnknownConstant(SemanticError):
    def __init__(self, pos, constname):
        self.pos = pos
        self.constname = constname

    @property
    def message(self):
        return f'Константа \'{self.constname}\' ранее не была объявлена'
