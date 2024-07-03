from cmp.utils import Token
from Lexer.Automatons import *
from Grammar import G
from TokensTable import get_token

class Lexer:
    def __init__(self):
        tokens = []
        automaton = None

    def Tokenize(self, G, text:str):
        words = text.split()
        for word in words:
            autom_result = self.automaton.evaluate(word)
            if autom_result[0]:
                self.tokens.append(autom_result[1])
            else:
                self.tokens.append(Token(word, G.UNKNOWN))
        self.tokens.append(Token('$', G.EOF))
        return self.tokens
    
class Lexer_Generator:
    def __init__(self):
        self.automaton = None
        self.tokens = []

    def Generate(self, G):
        for token in G.terminals:
            print(Token(get_token(token.Name), token.Name))
            # export_to_md(DFA.getDFA(Token(token.Name, G[token.Name])), "./automatasMD/"+token.Name+".md")


lexer = Lexer_Generator()
lexer.Generate(G)