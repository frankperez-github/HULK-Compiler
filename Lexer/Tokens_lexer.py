import Grammar.Grammar as Gr

tokens = [
    (Gr.obra, '\{'),
    (Gr.cbra, '\}'),
    (Gr.opar, '\('),
    (Gr.cpar, '\)'),
    (Gr.ocor, '\['),
    (Gr.ccor, '\]'),
    (Gr.d_bar, '\|\|'),
    
    (Gr.dot, '\.'),
    (Gr.semi, ','),
    (Gr.colon, ':'),
    (Gr.semicolon, ';'),
    (Gr.arrow, '=>'),
    
    (Gr.or_, '\|'),
    (Gr.and_, '&'),
    (Gr.not_, '!'),
    
    (Gr.d_as, ':='),
    (Gr.s_as, '='),
    (Gr.new_, 'new'),
    
    (Gr.eq, '=='),
    (Gr.neq, '!='),
    (Gr.leq, '<='),
    (Gr.geq, '>='),
    (Gr.lt, '<'),
    (Gr.gt, '>'),
    
    (Gr.is_, 'is'),
    (Gr.as_, 'as'),
    
    (Gr.arr, '@'),
    (Gr.d_arr, '@@'),
    
    (Gr.plus, '\+'),
    (Gr.minus, '\-'),
    (Gr.star, '\*'),
    (Gr.div, '/'),
    (Gr.mod, '%'),
    (Gr.pow_, '\^'),
    (Gr.pow__, '\*\*'),
    
    (Gr.bool_, 'true|false'),
    (Gr.str_, '("([\x00-!#-\x7f]|\\\\")*"|\\"([\x00-!#-\x7f]|\\\\")*\\"")'),
    (Gr.number_, '(0|[1-9][0-9]*)(.[0-9]+)?'),
    
    (Gr.let_, 'let'),
    (Gr.in_, 'in'),
    
    (Gr.if_, 'if'),
    (Gr.else_, 'else'),
    (Gr.elif_, 'elif'),
    
    (Gr.while_, 'while'),
    (Gr.for_, 'for'),
    
    (Gr.inherits, 'inherits'),
    (Gr.function, 'function'),
    (Gr.protocol, 'protocol'),
    (Gr.extends, 'extends'),
    (Gr.type_, 'type'),
    (Gr.base_, 'base'),

    (Gr.id_, '[_a-zA-Z][_a-zA-Z0-9]*'),
]