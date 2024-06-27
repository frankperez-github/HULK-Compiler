from abc import ABC
from cmp.semantic import Scope

class Node(ABC):
    def __init__(self):
        self.scope: Scope

class ProgramNode(Node):
    def __init__(self, declarations, expression):
        super().__init__()
        self.declarations = declarations
        self.expression = expression

class ExpressionNode(Node):
    pass

class DeclarationNode(Node):
    pass

class VectorTypeAnnotationNode(Node):
    def __init__(self, element_type):
        super().__init__()
        self.element_type = element_type

class FunctionDeclarationNode(DeclarationNode):
    def __init__(self, id_, params, expr, return_type=None):
        super().__init__()
        self.id = id_
        self.params= params
        self.expr = expr
        self.return_type = return_type

class TypeDeclarationNode(DeclarationNode):
    def __init__(self, id_, params, body, parent, parent_args=None):
        super().__init__()
        self.id = id_
        self.methods = [method for method in body if isinstance(method, FunctionDeclarationNode)]
        self.attributes = [attribute for attribute in body if isinstance(attribute, AttributeDeclarationNode)]
        self.params=params
        self.parent = parent
        self.parent_args = parent_args

class AttributeDeclarationNode(DeclarationNode):
    def __init__(self, id_, expr, attribute_type=None):
        super().__init__()
        self.id = id_
        self.expr = expr
        self.attribute_type = attribute_type

class MethodDeclarationNode(DeclarationNode):
    def __init__(self, id_, params, return_type):
        super().__init__()
        self.id = id_
        self.params = params
        self.return_type = return_type

class ProtocolDeclarationNode(DeclarationNode):
    def __init__(self, id_, methods_signature, parent):
        super().__init__()
        self.id = id_
        self.methods_signature = methods_signature
        self.parent = parent

class VarDeclarationNode(DeclarationNode):
    def __init__(self, id_, expr, var_type=None):
        super().__init__()
        self.id = id_
        self.expr = expr
        self.var_type = var_type

class TypeInstantiationNode(ExpressionNode):
    def __init__(self, id_, args):
        super().__init__()
        self.id = id_
        self.args = args

class ExpressionBlockNode(ExpressionNode):
    def __init__(self, expressions):
        super().__init__()
        self.expressions = expressions

class AtomicNode(ExpressionNode, ABC):
    def __init__(self, lex):
        super().__init__()
        self.lex = lex

class BinaryExpressionNode(ExpressionNode, ABC):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right
        self.operator = None

class UnaryExpressionNode(ExpressionNode, ABC):
    def __init__(self, operand):
        super().__init__()
        self.operand = operand
        self.operator = None

class DestructiveAssignmentNode(ExpressionNode):
    def __init__(self, id_, expr):
        super().__init__()
        self.id = id_
        self.expr = expr

class WhileNode(ExpressionNode):
    def __init__(self, condition, expression):
        super().__init__()
        self.condition = condition
        self.expression = expression

class ForNode(ExpressionNode):
    def __init__(self, var, iterable, expression):
        super().__init__()
        self.var = var
        self.iterable = iterable
        self.expression = expression

class LetInNode(ExpressionNode):
    def __init__(self, var_declarations, body):
        super().__init__()
        self.var_declarations = var_declarations
        self.body = body

class ConditionalNode(ExpressionNode):
    def __init__(self, condition, expression, else_expr):
        super().__init__()
        self.condition = condition
        self.expression = expression
        self.else_expr = else_expr

class IsNode(ExpressionNode):
    def __init__(self, expression, type_):
        super().__init__()
        self.expression = expression
        self.type = type_

class AsNode(ExpressionNode):
    def __init__(self, expression, type_):
        super().__init__()
        self.expression = expression
        self.type = type_

class FunctionCallNode(ExpressionNode):
    def __init__(self, id_, args):
        super().__init__()
        self.id = id_
        self.args = args

class AttributeCallNode(ExpressionNode):
    def __init__(self, obj, attribute):
        super().__init__()
        self.obj = obj
        self.attribute = attribute

class MethodCallNode(ExpressionNode):
    def __init__(self, obj, method, args):
        super().__init__()
        self.obj = obj
        self.method = method
        self.args = args

class VectorInitializationNode(ExpressionNode):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

class VectorComprehensionNode(ExpressionNode):
    def __init__(self, function_, var, iterable):
        super().__init__()
        self.function = function_
        self.var = var
        self.iterable = iterable

class IndexingNode(ExpressionNode):
    def __init__(self, obj, index):
        super().__init__()
        self.obj = obj
        self.index = index

class BaseCallNode(ExpressionNode):
    def __init__(self, args):
        super().__init__()
        self.args = args

class ConstantNumNode(AtomicNode):
    pass

class ConstantBoolNode(AtomicNode):
    pass

class ConstantStringNode(AtomicNode):
    pass

class VariableNode(AtomicNode):
    pass

class StringBinaryExpressionNode(BinaryExpressionNode, ABC):
    pass

class BoolBinaryExpressionNode(BinaryExpressionNode, ABC):
    pass

class InequalityExpressionNode(BinaryExpressionNode, ABC):
    pass

class ArithmeticExpressionNode(BinaryExpressionNode, ABC):
    pass

class EqualityExpressionNode(BinaryExpressionNode, ABC):
    pass

class ConcatNode(StringBinaryExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '@'

class DoubleConcatNode(StringBinaryExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '@@'

class NotNode(UnaryExpressionNode):
    def __init__(self,expr):
        super().__init__(expr)
        self.operator = '!'

class NegNode(UnaryExpressionNode):
    def __init__(self,expr):
        super().__init__(expr)
        self.operator = '-'

class OrNode(BoolBinaryExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '|'

class AndNode(BoolBinaryExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '&'

class LessThanNode(InequalityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '<'

class GreaterThanNode(InequalityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '>'

class LessOrEqualNode(InequalityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '<='

class GreaterOrEqualNode(InequalityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '>='

class PlusNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '+'

class MinusNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '-'

class StarNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '*'

class DivNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '/'

class ModNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '%'

class PowNode(ArithmeticExpressionNode):
    def __init__(self, left, right, operator):
        super().__init__(left, right)
        self.operator = operator

class EqualNode(EqualityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '=='

class NotEqualNode(EqualityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '!='