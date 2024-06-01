import ply.yacc as yacc
from Lexer import tokens
    
# Precedencia de operaciones
precedence = (
    ('left', 'PLUS', 'MINUS'), 
    ('left', 'STAR', 'DIVIDE'), 
)

# Reglas de la gramática
def p_expression(p):
    '''expression : expression PLUS term
                  | expression MINUS term
                  | term'''
    print("e")
    
    if len(p) == 4:
        print(p[0],p[1],p[2],p[3])
        p[0] = (p[2], p[1], p[3])
    elif len(p) == 2:
        print(p[0],p[1])
        p[0] = p[1]

def p_term(p):
    '''term : term STAR factor
            | term DIVIDE factor
            | factor '''
    print("t")
    
    if len(p) == 4:
        print(p[0],p[1],p[2],p[3])
        p[0] = (p[2], p[1], p[3])

    elif len(p) == 2:
        print(p[0],p[1])
        p[0] = p[1]

def p_factor(p):
    '''factor : NUMBER
              | LPAREN expression RPAREN'''
    
    print("f")
    print(p[0],p[1])
    if len(p) == 2:
        p[0] = p[1]
    else:  # Caso para paréntesis
        p[0] = p[2]

def p_error(p):
    print(f"Syntax error at '{p.value}'")

# Construir el parser
parser = yacc.yacc()

print(parser.parse('3.14  + 4.3'))