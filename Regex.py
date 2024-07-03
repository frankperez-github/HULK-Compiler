from Automatons import *
from cmp.ast import *
from cmp.pycompiler import Grammar
from cmp.utils import Token
from cmp.evaluation import evaluate_reverse_parse


class EpsilonNode(AtomicNode):
    def evaluate(self):
        start_state = State('0')
        return NDFA(start_state=start_state, final_states=[start_state])
    
class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        start_state = State('0')
        final_state = State('1')
        start_state.set_transition(s, final_state)
        return NDFA(start_state, [final_state])    

class UnionNode(BinaryNode):
    def operate(self, lvalue, rvalue):        
        return NDFA.union(lvalue, rvalue)

class ConcatenationNode(BinaryNode):
    def operate(self, lvalue, rvalue):        
        return NDFA.concatenation(lvalue, rvalue)
    
class ClosureNode(UnaryNode):
    def operate(self, value: NDFA):        
        return value.closure()

class PositiveClosureNode(UnaryNode):
    def operate(self, value: NDFA):        
        return NDFA.concatenation(value, value.closure())
    
class Zero_OneNode(UnaryNode):
    def operate(self, value: NDFA):        
        return NDFA.union(value, EpsilonNode(G.EOF).evaluate())
    
class CharNode(Node):
    def __init__(self, symbols: list[SymbolNode]) -> None:
        self.symbols = symbols

    def evaluate(self):
        value = self.symbols[0].evaluate()  
        for symbol in self.symbols[1:]:            
            value = NDFA.union(value, symbol.evaluate())  
        return value

class RangeNode(Node):
    def __init__(self, first: SymbolNode, last: SymbolNode) -> None:
        self.first = first
        self.last = last

    def evaluate(self):
        value = [self.first.evaluate()]
        for i in range(ord(self.first.lex) + 1, ord(self.last.lex)):
            value.append(SymbolNode(chr(i)).evaluate())
        value.append(self.last.evaluate())
        
        combined_value = value[0]
        for val in value[1:]:
            combined_value = NDFA.union(combined_value, val)
        return combined_value

G = Grammar()

E = G.NonTerminal('E', True)
T, F, A, S = G.NonTerminals('T F A S')
pipe, star, plus, minus, quest, opar, cpar, obrack, cbrack, symbol, epsilon = G.Terminals('| * + - ? ( ) [ ] symbol ε')


E %= T, lambda h,s: s[1]
E %= E + pipe + T, lambda h,s: UnionNode(s[1],s[3])

T %= F, lambda h,s: s[1]
T %= T + F, lambda h,s: ConcatenationNode(s[1],s[2])

F %= A, lambda h,s: s[1]
F %= A + star, lambda h,s: ClosureNode(s[1])
F %= A + plus, lambda h,s: PositiveClosureNode(s[1])
F %= A + quest, lambda h,s: Zero_OneNode(s[1])

A %= symbol, lambda h,s: SymbolNode(s[1])
A %= epsilon, lambda h,s: EpsilonNode(s[1])                                                
A %= opar + E + cpar, lambda h,s: s[2]
A %= obrack + S + cbrack, lambda h,s: CharNode(s[2])

S %= symbol, lambda h,s: [SymbolNode(s[1])]
S %= symbol + S, lambda h,s: [SymbolNode(s[1])] + s[2]
S %= symbol + minus + symbol, lambda h,s: RangeNode(SymbolNode(s[1]),SymbolNode(s[3])).evaluate()
S %= symbol + minus + symbol + S, lambda h,s: RangeNode(SymbolNode(s[1]),SymbolNode(s[3])).evaluate() + s[4]


