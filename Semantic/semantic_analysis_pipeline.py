from type_collector import TypeCollector
from type_builder import TypeBuilder
from type_cheker_vars import VarCollector
from type_infererer import TypeInferrer
from type_cheker import TypeChecker



def semantic_analysis_pipeline(ast, debug=False):
    if debug:
        print('============== COLLECTING TYPES ===============')
    errors = []
    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('=============== BUILDING TYPES ================')
    builder = TypeBuilder(context, errors)
    builder.visit(ast)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('=============== CHECKING TYPES ================')
        print('---------------- COLLECTING VARIABLES ------------------')
    var_collector = VarCollector(context, errors)
    scope = var_collector.visit(ast)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('Scope:')
        print(scope)
        print('---------------- INFERRING TYPES ------------------')
    type_inferrer = TypeInferrer(context, errors)
    type_inferrer.visit(ast)
    # Check if there are any inference errors and change the types to ErrorType if there are
    inference_errors = context.inference_errors() + scope.inference_errors()
    errors.extend(inference_errors)
    if debug:
        print('Iterations: ' + str(type_inferrer.current_iteration))
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('Scope:')
        print(scope)
        print('---------------- CHECKING TYPES ------------------')
    type_checker = TypeChecker(context, errors)
    type_checker.visit(ast)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('Scope:')
        print(scope)
    return ast, errors, context, scope
