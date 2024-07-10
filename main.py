import subprocess
import sys
from pathlib import Path
import errors
from Lexer.Lexer_generator import Lexer
from Parser.Parser import ParserError, LR1Parser
from Parser.HulkParser import HulkParser
from Grammar.Grammar import G
from Grammar import Grammar as Gr
from Lexer.Tokens_lexer import tokens
from Semantic.semantic_analysis_pipeline import semantic_analysis_pipeline
from Code_gen.code_generator import CCodeGenerator
from cmp.evaluation import evaluate_reverse_parse
import dill
import os


def save_object(automaton, file_path):
    with open(file_path, 'wb') as file:
        dill.dump(automaton, file)  # Cambia 'object' por 'automaton'

def load_object(file_path):
    with open(file_path, 'rb') as file:
        loaded_object = dill.load(file)  # Cambia 'object' por 'loaded_object'
    return loaded_object

def print_error(message):
    red = "\033[31m"
    refresh = "\033[0m"
    print(f"{red}{message}{refresh}")


def run_pipeline(input_path: Path, output_path: Path):
    sys.setrecursionlimit(1000000000)
    if not input_path.match('*.hulk'):
        raise errors.HulkIOError(errors.HulkIOError.INVALID_EXTENSION % input_path)

    try:
        with open(input_path) as f:
            text = f.read()
    except FileNotFoundError:
        error = errors.HulkIOError(errors.HulkIOError.ERROR_READING_FILE % input_path)
        print_error(error)
        return
    
    #if os.path.isfile("Lexer/hulk_lexer.pkl"):
    #    lexer=load_object("Lexer/hulk_lexer.pkl")
    #else:
    #    lexer= Lexer(tokens,G.EOF)  
    #    save_object(lexer,"Lexer/hulk_lexer.pkl")

    lexer= Lexer(tokens,G.EOF)

    try:
        tokens_=lexer.tokenize(text)
    except errors.LexerError as e:
        print_error(e)
        return

    
    #parser = HulkParser(True,True)


    #if os.path.isfile("Parser/hulk_parser_action.pkl"):
    #    parser=load_object("Parser/hulk_parser_action.pkl")
    #else:
    #    parser=LR1Parser(G)    
    #    save_object(parser,"Parser/hulk_parser_action.pkl")

    parser=LR1Parser(G) 



    try: 
        parse, operations = parser([t.token_type for t in tokens_])
    except ParserError as e:
        error_token = tokens_[e.token_index]
        error_text = errors.HulkSyntacticError.PARSING_ERROR % error_token.lex
        error_ = [errors.HulkSyntacticError(error_text, error_token.row, error_token.column,)]
        print_error(error_)
        return
    
    ast=evaluate_reverse_parse(parse,operations,tokens_)

    semantic_ast, semantic_errors,context,_=semantic_analysis_pipeline(ast)

    if semantic_errors:
        for e in semantic_errors:
            print_error(e)
        return
    
    codegen=CCodeGenerator()
    code= codegen(semantic_ast,context)

    try:
        with open(output_path, 'w') as f:
            f.write(code)
    except FileNotFoundError:
        error = errors.HulkIOError(errors.HulkIOError.ERROR_WRITING_FILE % output_path)
        print_error(error)
        return
    
    
    subprocess.run(["gcc","-o",input_name,input_name+'.c', "-lm"])
    subprocess.run(['./%s'%input_name])
    


if __name__ == "__main__":
    input = sys.argv[1]
    input_path = Path(input)
    input_name = input_path.stem
    output_file = Path(f'{input_name}.c')
    run_pipeline(input_path, output_file)




    