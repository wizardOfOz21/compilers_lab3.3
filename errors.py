import parser_edsl as pe

class SemanticError(pe.Error):
    pass

class SubrangeBordersTypeMismatch(SemanticError):
    def __init__(self, pos):
        self.pos = pos

    @property
    def message(self):
        return f'Типы границ диапазона не целые'
    
class SubrangeWrongBorders(SemanticError):
    def __init__(self, pos):
        self.pos = pos

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
    
class RepeatedRecordField(SemanticError):
    def __init__(self, pos, fieldname, prev_def_pos):
        self.pos = pos
        self.fieldname = fieldname
        self.prev_def = prev_def_pos

    @property
    def message(self):
        return f'Поле \'{self.fieldname}\' уже было объявлено ранее в записи: {self.prev_def}'

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

class SignedString(SemanticError):
    def __init__(self, sign_pos, name):
        self.pos = sign_pos
        self.name = name

    @property
    def message(self):
        return f'Знак перед константой со значением строки: {self.name}'
