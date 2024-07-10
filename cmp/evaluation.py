from cmp.pycompiler import EOF
from Parser.Parser import ShiftReduceParser

def evaluate_reverse_parse(right_parse, operations, tokens):
    if not right_parse or not operations or not tokens:
        return

    right_parse = iter(right_parse)
    tokens = iter(tokens)
    stack = []
    line=None
    column=None

    for operation in operations:
        if operation == ShiftReduceParser.SHIFT:
            token = next(tokens)
            stack.append(token.lex)
            line=str(token.row)
            column=str(token.column)
        elif operation == ShiftReduceParser.REDUCE:
            production = next(right_parse)
            head, body = production
            attributes = production.attributes
            assert all(rule is None for rule in attributes[1:]), 'There must be only synteticed attributes.'
            rule = attributes[0]

            if len(body):
                synteticed = [None] + stack[-len(body):]
                value = rule(None, synteticed)
                if(hasattr(value,'line') and hasattr(value,'column')):
                    value.line=line
                    value.column=column
                stack[-len(body):] = [value]
            else:
                value=rule(None,None)
                if(hasattr(value,'line') and hasattr(value,'column')):
                    value.line=line
                    value.column=column
                stack.append(value)
        else:
            raise Exception('Invalid action!!!')

    assert len(stack) == 1
    assert isinstance(next(tokens).token_type, EOF)
    return stack[0]