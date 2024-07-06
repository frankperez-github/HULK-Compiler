from Lexer.Lexer_generator import Lexer

tokens = [
    ("obra", '\{'),
    ("cbra", '\}'),
    ("opar", '\('),
    ("cpar", '\)'),
    ("ocor", '\['),
    ("ccor", '\]'),
    ("d_bar", '\|\|'),
    
    ('space', '  *'),
    ("dot", '\.'),
    ("semi", ','),
    ("colon", ':'),
    ("semicolon", ';'),
    ("arrow", '=>'),
    
    ("or_", '\|'),
    ("and_", '&'),
    ("not_", '!'),
    
    ("d_as", ':='),
    ("s_as", '='),
    ("new_", 'new'),
    
    ("eq", '=='),
    ("neq", '!='),
    ("leq", '<='),
    ("geq", '>='),
    ("lt", '<'),
    ("gt", '>'),
    
    ("is_", 'is'),
    ("as_", 'as'),
    
    ("arr", '@'),
    ("d_arr", '@@'),
    
    ("plus", '\+'),
    ("minus", '\-'),
    ("star", '\*'),
    ("div", '/'),
    ("mod", '%'),
    ("pow_", '\^'),
    ("pow__", '\*\*'),
    
    ("bool_", 'true|false'),
    ("str_", '"([\x00-!#-\x7f]|\\\\")*"'),
    ("number_", '(0|[1-9][0-9]*)(.[0-9]+)?'),
    ('comment','//[\x00-\x09\x0b-\x7f]*\n'),
    
    ("let_", 'let'),
    ("in_", 'in'),
    
    ("if_", 'if'),
    ("else_", 'else'),
    ("elif_", 'elif'),
    
    ("while_", 'while'),
    ("for_", 'for'),
    
    ("print", 'print'),
    ("inherits", 'inherits'),
    ("function", 'function'),
    ("protocol", 'protocol'),
    ("extends", 'extends'),
    ("type_", 'type'),
    ("base_", 'base'),
    ("endofline_",'\n'),

    ("id_", '[_a-zA-Z][_a-zA-Z0-9]*'),
]
text = """type person() {
                            name = "John";
                            age = 25;
                            
                           printName(){
                                print(name);
                            }
                        }
                        
                        let x = new Person() in if (x.name == "Jane") print("Jane") else print("John");"""

lexer = Lexer(tokens,"$")
for token in lexer.tokenize(text):
    print(token)