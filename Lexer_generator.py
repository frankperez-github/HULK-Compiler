from cmp import Token
from Automatons import *

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
        self.tokens = []
        self.automaton = None

    def Generate(self, G):
        for token in G.terminals:
            export_to_md(DFA.getDFA(token.lex), token.lex+".md")