import subprocess
import sys
from pathlib import Path
import errors
from Lexer.Lexer_generator import Lexer
from Parser.Parser import LR1Parser, ParserError
from Grammar.Grammar import G
from Grammar import Grammar as Gr
from Lexer.Tokens_lexer import tokens
from Semantic.semantic_analysis_pipeline import semantic_analysis_pipeline
from Code_gen.code_generator import CCodeGenerator
from cmp.evaluation import evaluate_reverse_parse



def print_error(message):
    red = "\033[31m"
    refresh = "\033[0m"
    print(f"{red}{message}{refresh}")


def run_pipeline(input_path: Path, output_path: Path):
    if not input_path.match('*.hulk'):
        raise errors.HulkIOError(errors.HulkIOError.INVALID_EXTENSION % input_path)

    try:
        with open(input_path) as f:
            text = f.read()
    except FileNotFoundError:
        error = errors.HulkIOError(errors.HulkIOError.ERROR_READING_FILE % input_path)
        print_error(error)
        return
    
    lexer= Lexer(tokens,G.EOF)

    try:
        tokens_=lexer.tokenize(text)
    except errors.LexerError as e:
        print_error(e)
        return
<<<<<<< HEAD
    
=======

>>>>>>> b65e6e7ab1542a9ea0ed8e7bf4ee873ef53acd11
    parser = LR1Parser(G)

    try: 
        parse, operations = parser([t.token_type for t in tokens_])
    except ParserError as e:
        error_token = tokens_[e.token_index]
        error_text = errors.HulkSyntacticError.PARSING_ERROR % error_token.lex
<<<<<<< HEAD
        error_ = [errors.HulkSyntacticError(error_text, error_token.column, error_token.row)]
=======
        error_ = [errors.HulkSyntacticError(error_text, error_token.row, error_token.column,)]
>>>>>>> b65e6e7ab1542a9ea0ed8e7bf4ee873ef53acd11
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
    
<<<<<<< HEAD


if __name__ == "__main__":
    inp = sys.argv[1]
    input_path = Path(inp)
    input_file_name = input_path.stem
    output_file = Path(f'{input_file_name}.c')
=======
    
    subprocess.run(["gcc","-o",input_name,input_name+'.c', "-lm"])
    subprocess.run(['./%s'%input_name])
    


if __name__ == "__main__":
    input = sys.argv[1]
    input_path = Path(input)
    input_name = input_path.stem
    output_file = Path(f'{input_name}.c')
>>>>>>> b65e6e7ab1542a9ea0ed8e7bf4ee873ef53acd11
    run_pipeline(input_path, output_file)


    