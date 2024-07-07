from Grammar.Grammar import G
from Parser.Parser import LR1Parser, ParserError
from errors import HulkSyntacticError
import dill

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
            #sys.setrecursionlimit(10000)
            with open('Parser/hulk_parser_action.pkl', 'wb') as action_pkl:
                dill.dump(self.action, action_pkl)
            with open('Parser/hulk_parser_goto.pkl', 'wb') as goto_pkl:
                dill.dump(self.goto, goto_pkl)
            with open('Parser/hulk_parser_verbose.pkl', 'wb') as verbose_pkl:
                dill.dump(self.verbose, verbose_pkl)
    
    def __call__(self, w):
        super.__call__(w)
        
    
