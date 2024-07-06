from Lexer.Automatons import *
from cmp.ast import *
from cmp.pycompiler import Grammar
from cmp.utils import Token
from Parser.Parser import LR1Parser
from cmp.evaluation import evaluate_reverse_parse


class Epsilon(AtomicNode):
    def evaluate(self):
        return NDFA(states=1, finals=[0], transitions={})
    
class Symbol(AtomicNode):
    def evaluate(self):
        s = self.lex
        return NDFA(states=2, finals=[1], transitions={(0, s): [1]})    
    
class Union(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):        
        return NDFA.union(lvalue,rvalue)

class Concatenation(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):        
        return NDFA.concatenation(lvalue,rvalue)
    
class Closure(UnaryNode):
    @staticmethod
    def operate(value: NDFA):        
        return value.closure()

class PositiveClosure(UnaryNode):
    @staticmethod
    def operate(value: NDFA):        
        return NDFA.concatenation(value,value.closure())
    
class Zero_One(UnaryNode):
    @staticmethod
    def operate(value: NDFA):        
        return NDFA.union(value,Epsilon(G.EOF).evaluate())
    
class Char(Node):
    def __init__(self, symbols: list[Symbol]) -> None:
        self.symbols = symbols

    def evaluate(self):
        value = self.symbols[0].evaluate()  
        for symbol in self.symbols[1:]:            
            value = value.union(symbol.evaluate())  
        return value

class Range(Node):
    def __init__(self, first: Symbol, last: Symbol) -> None:
        self.first = first
        self.last = last

    def evaluate(self):
        value = [self.first]
        for i in range(ord(self.first.lex)+1,ord(self.last.lex)):
            value.append(Symbol(chr(i)))
        value.append(self.last)
        return value      
          
    


G = Grammar()

E = G.NonTerminal('E', True)
T, F, A, S = G.NonTerminals('T F A S')
pipe, star, plus, minus, quest, opar, cpar, obrack, cbrack, symbol, epsilon = G.Terminals('| * + - ? ( ) [ ] symbol ε')



F %= A, lambda h,s: s[1]
F %= A + star, lambda h,s: Closure(s[1])
F %= A + plus, lambda h,s: PositiveClosure(s[1])
F %= A + quest, lambda h,s: Zero_One(s[1])

A %= symbol, lambda h,s: Symbol(s[1])
A %= epsilon, lambda h,s: Epsilon(s[1])                                                
A %= opar + E + cpar, lambda h,s: s[2]
A %= obrack + S + cbrack, lambda h,s: Char(s[2])

S %= symbol, lambda h,s: [Symbol(s[1])]
S %= symbol + S, lambda h,s: [Symbol(s[1])] + s[2]
S %= symbol + minus + symbol, lambda h,s: Range(Symbol(s[1]),Symbol(s[3])).evaluate()
S %= symbol + minus + symbol + S, lambda h,s: Range(Symbol(s[1]),Symbol(s[3])).evaluate() + s[4]

E %= T, lambda h,s: s[1]
E %= E + pipe + T, lambda h,s: Union(s[1],s[3])

T %= F, lambda h,s: s[1]
T %= T + F, lambda h,s: Concatenation(s[1],s[2])




regex_parser = LR1Parser(G)


class Regex:
    def __init__(self, text: str) -> None:
        self.text = text
        self.automaton = self._build_automaton()       


    def __call__(self, w: str) -> bool:
        return self.automaton.recognize(w) 


    def tokenize_regex(self):
        tokens = []

        fixed_tokens = {lex: Token(lex,G[lex]) for lex in '( ) [ ] * + - ε | ?  symbol '.split()}
    
        char_class = escape = False    

        for char in self.text:

            if escape:
                tokens.append(Token(char, symbol))
                escape = False
                continue

            if char == ']':
                char_class = False            
            elif char_class:
                if char != '-':
                    tokens.append(Token(char, symbol))
                    continue
            elif char == '[':
                char_class = True
            elif char == '\\':
                escape = True
                continue
            
            try:
                token = fixed_tokens[char]
            except KeyError:
                token = Token(char, symbol)
            tokens.append(token)                 
            
        tokens.append(Token('$', G.EOF))
        return tokens
    
    
    def _build_automaton(self):
        tokens = self.tokenize_regex()     
        
        try:
            parse, operations = regex_parser([token.token_type for token in tokens])
        except TypeError:
            print(tokens) 
            raise TypeError

        ast = evaluate_reverse_parse(parse,operations,tokens)
        ndfa = ast.evaluate()
        dfa = ndfa.to_DFA()
        return dfa