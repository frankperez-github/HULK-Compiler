from cmp.utils import Token
from cmp.automata import State
from Lexer.Regex import Regex
from errors import *


class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self.make_regex_automatons(table)
        self.automaton = self.make_automaton()

    
    def make_regex_automatons(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            automaton = Regex(regex).automaton
            automaton = State.from_nfa(automaton)
            for state in automaton:
                if state.final:
                    state.tag = (n,token_type)
            regexs.append(automaton)
        return regexs
    
    
    def make_automaton(self):
        start = State('start')
        for automaton in self.regexs:
            start.add_epsilon_transition(automaton)
        return start.to_deterministic()
    
        
    def evaluate(self, string):
        state = self.automaton
        final = state if state.final else None
        lex = ''
        final_lex = ''

        for char in string:
            lex += char
            try:
                state = state.get(char)
                if state.final:
                    final = state
                    final_lex = lex                    
            except KeyError:
                break
            
        return final, final_lex
    
    
    def tokenize(self, text):
        return [token for token in self.tokens_generator(text)]


    def tokens_generator(self, text):
        rows = text.split('\n')
        row = 0
        column = 1
        while text:
            
            final_state, lex = self.evaluate(text)
            if len(lex) == 0: 
                return LexerError("Error found with token's lex", column=column, row=row)

            _, token_type = [state.tag for state in final_state.state if state.tag][0]
            
            text = text[len(lex):]

            if len(lex.split(' ')) == 1:
                yield Token(lex=lex, token_type=token_type, column=column, row=row)

            column += len(lex)
            if column > len(rows[row])+1: 
                row += 1
                column = 0

        
        yield Token("$", self.eof, column=column, row=row)    
    