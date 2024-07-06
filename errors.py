class LexerError(Exception):
    def __init__(self, error_message, col, row):
        self.row = row
        self.col = col
        self.error_message = error_message

    def __str__(self):
        return f'Syntatic Error on line: {self.row}, col: {self.col}. Error message: {self.error_message}'

class HulkError(Exception):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'HulkError'

    @property
    def text(self):
        return self.args[0]

    def __str__(self):
        return f'{self.error_type}: {self.text}'

    def __repr__(self):
        return str(self)


class HulkIOError(HulkError):
    INVALID_EXTENSION = 'Input file \'%s\' is not a .hulk file.'
    ERROR_READING_FILE = 'Error reading file \'%s\'.'
    ERROR_WRITING_FILE = 'Error writing to file \'%s\'.'

    @property
    def error_type(self):
        return 'IOHulkError'


class HulkSyntacticError(HulkError):
    def __init__(self, text, line, column):
        super().__init__(text)
        self.line = line
        self.column = column

    def __str__(self):
        return f'({self.line}, {self.column}) - {self.error_type}: {self.text}'

    PARSING_ERROR = 'Error at or near \'%s\'.'

    @property
    def error_type(self):
        return 'SyntacticError'


class HulkSemanticError(HulkError):
    WRONG_SIGNATURE = 'Method \'%s\' already defined in an ancestor with a different signature.'
    SELF_IS_READONLY = 'Variable "self" is read-only.'
    INCOMPATIBLE_TYPES = 'Cannot convert \'%s\' into \'%s\'.'
    VARIABLE_NOT_DEFINED = 'Variable \'%s\' is not defined.'
    INVALID_OPERATION = 'Operation \'%s\' is not defined between \'%s\' and \'%s\'.'
    INVALID_UNARY_OPERATION = 'Operation \'%s\' is not defined for \'%s\'.'
    INCONSISTENT_USE = 'Inconsistent use of \'%s\'.'
    EXPECTED_ARGUMENTS = 'Expected %s arguments, but got %s in \'%s\'.'
    CANNOT_INFER_PARAM_TYPE = 'Cannot infer type of parameter \'%s\' in \'%s\'. Please specify it.'
    CANNOT_INFER_ATTR_TYPE = 'Cannot infer type of attribute \'%s\'. Please specify it.'
    CANNOT_INFER_RETURN_TYPE = 'Cannot infer return type of \'%s\'. Please specify it.'
    CANNOT_INFER_VAR_TYPE = 'Cannot infer type of variable \'%s\'. Please specify it.'
    BASE_OUTSIDE_METHOD = 'Cannot use "base" outside of a method.'
    METHOD_NOT_DEFINED = 'Method \'%s\' is not defined in any ancestor.'

    @property
    def error_type(self):
        return 'SemanticError'
