from ply import lex
from Grammar import G

#tokens=G.terminals

tokens = [
    'NUMBER',
    'PLUS',
    'MINUS',
    'STAR',
    'DIVIDE',
    'LPAREN',
    'RPAREN'
]

# Expresiones regulares para tokens simples
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_STAR   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'


# Expresión regular para números
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de errores léxicos
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


# Construcción del lexer
lexer = lex.lex()

