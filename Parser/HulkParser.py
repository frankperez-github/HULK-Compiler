from Grammar.Grammar import G
from Parser.Parser import LR1Parser, ParserError
from typing import List
from cmp.utils import Token
from errors import HulkSyntacticError
import sys
import dill
import errors


class HulkParser(LR1Parser):
    def __init__(self, rebuild = False, save =False):
        if rebuild: super().__init__(G)
        else:
            try:
                with open('Parser/hulk_parser_action.pkl', 'rb') as action_pkl:
                    self.action = dill.load(action_pkl)
                with open('Parser/hulk_parser_goto.pkl', 'rb') as goto_pkl:
                    self.goto = dill.load(goto_pkl)
                with open('Parser/hulk_parser_verbose.pkl', 'rb') as verbose_pkl:
                    self.verbose = dill.load(verbose_pkl)
            except:
                super().__init__(G)
                
                
        if save:
            
            with open('Parser/hulk_parser_action.pkl', 'wb') as action_pkl_:
                dill.dump(self.action, action_pkl_)
            with open('Parser/hulk_parser_goto.pkl', 'wb') as goto_pkl_:
                dill.dump(self.goto, goto_pkl_)
            with open('Parser/hulk_parser_verbose.pkl', 'wb') as verbose_pkl_:
                dill.dump(self.verbose, verbose_pkl_)
    
        
    
