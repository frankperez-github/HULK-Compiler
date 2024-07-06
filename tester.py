from Lexer.Lexer_generator import Lexer
import Grammar

tokens = [
    (Grammar.obra, '\{'),
    (Grammar.cbra, '\}'),
    (Grammar.opar, '\('),
    (Grammar.cpar, '\)'),
    (Grammar.ocor, '\['),
    (Grammar.ccor, '\]'),
    (Grammar.d_bar, '\|\|'),
    
    (Grammar.dot, '\.'),
    (Grammar.semi, ','),
    (Grammar.colon, ':'),
    (Grammar.semicolon, ';'),
    (Grammar.arrow, '=>'),
    
    (Grammar.or_, '\|'),
    (Grammar.and_, '&'),
    (Grammar.not_, '!'),
    
    (Grammar.d_as, ':='),
    (Grammar.s_as, '='),
    (Grammar.new_, 'new'),
    
    (Grammar.eq, '=='),
    (Grammar.neq, '!='),
    (Grammar.leq, '<='),
    (Grammar.geq, '>='),
    (Grammar.lt, '<'),
    (Grammar.gt, '>'),
    
    (Grammar.is_, 'is'),
    (Grammar.as_, 'as'),
    
    (Grammar.arr, '@'),
    (Grammar.d_arr, '@@'),
    
    (Grammar.plus, '\+'),
    (Grammar.minus, '\-'),
    (Grammar.star, '\*'),
    (Grammar.div, '/'),
    (Grammar.mod, '%'),
    (Grammar.pow_, '\^'),
    (Grammar.pow__, '\*\*'),
    
    (Grammar.bool_, 'true|false'),
    (Grammar.str_, '"([\x00-!#-\x7f]|\\\\")*"'),
    (Grammar.number_, '(0|[1-9][0-9]*)(.[0-9]+)?'),
    
    (Grammar.let_, 'let'),
    (Grammar.in_, 'in'),
    
    (Grammar.if_, 'if'),
    (Grammar.else_, 'else'),
    (Grammar.elif_, 'elif'),
    
    (Grammar.while_, 'while'),
    (Grammar.for_, 'for'),
    
    (Grammar.inherits, 'inherits'),
    (Grammar.function, 'function'),
    (Grammar.protocol, 'protocol'),
    (Grammar.extends, 'extends'),
    (Grammar.type_, 'type'),
    (Grammar.base_, 'base'),

    (Grammar.id_, '[_a-zA-Z][_a-zA-Z0-9]*'),
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
print(lexer.tokenize(text))