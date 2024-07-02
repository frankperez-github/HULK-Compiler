import AST_nodes as nodes
import cmp.visitor as visitor
from errors import HulkSemanticError
from utils import Context, Scope, Function, VariableInfo
from types_ import ErrorType, AutoType, Method, SelfType


class VarCollector(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.errors: list = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass


    @visitor.when(nodes.ProgramNode)
    def visit(self, node:nodes.ProgramNode, scope: Scope = None):
        scope = Scope()
        node.scope = scope

        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())

        self.visit(node.expression, scope.create_child())

        return scope
    
    
    @visitor.when(nodes.TypeDeclarationNode)
    def visit(self, node: nodes.TypeDeclarationNode, scope: Scope):
        node.scope = scope

        self.current_type = self.context.get_type(node.id)

        if self.current_type.is_error():
            return

        # Set parent arguments when they are None
        if node.parent_args is None:
            node.parent_args = []

        # Set params cause in the type builder I didn't have the params of my parent
        if node.parent_args == [] and node.params_ids == []:
            self.current_type.set_params()
            node.params_ids, node.params_types = self.current_type.params_names, self.current_type.params_types
            # After this I know that my parent's args are my params (are just variables with its params names)
            node.parent_args = [nodes.VariableNode(param_name) for param_name in self.current_type.params_names]

        # Create a new scope that includes the parameters
        new_scope = scope.create_child()

        for i, param_name in enumerate(self.current_type.params_names):
            param_type = self.current_type.params_types[i]
            new_scope.define_variable(param_name, param_type, is_parameter=True)
            self.current_type.param_vars.append(VariableInfo(param_name, param_type))

        for expr in node.parent_args:
            self.visit(expr, new_scope.create_child())

        for attr in node.attributes:
            self.visit(attr, new_scope.create_child())

        # Create a new scope that includes the self symbol
        methods_scope = scope.create_child()
        methods_scope.define_variable('self', SelfType(self.current_type))
        for method in node.methods:
            self.visit(method, methods_scope.create_child())

    @visitor.when(nodes.AttributeDeclarationNode)
    def visit(self, node: nodes.AttributeDeclarationNode, scope: Scope):
        node.scope = scope
        self.visit(node.expr, scope.create_child())

    @visitor.when(nodes.MethodDeclarationNode)
    def visit(self, node: nodes.MethodDeclarationNode, scope: Scope):
        node.scope = scope

        method: Method = self.current_type.get_method(node.id)

        new_scope = scope.create_child()

        for i, param_name in enumerate(method.param_names):
            param_type = method.param_types[i]
            new_scope.define_variable(param_name, param_type, is_parameter=True)
            method.param_vars.append(VariableInfo(param_name, param_type))

        self.visit(node.expr, new_scope)

    @visitor.when(nodes.FunctionDeclarationNode)
    def visit(self, node: nodes.FunctionDeclarationNode, scope: Scope):
        node.scope = scope

        function: Function = self.context.get_function(node.id)

        new_scope = scope.create_child()

        for i, param_name in enumerate(function.param_names):
            param_type = function.param_types[i]
            new_scope.define_variable(param_name, param_type, is_parameter=True)
            function.param_vars.append(VariableInfo(param_name, param_type))

        self.visit(node.expr, new_scope)

    @visitor.when(nodes.ExpressionBlockNode)
    def visit(self, node: nodes.ExpressionBlockNode, scope: Scope):
        block_scope = scope.create_child()
        node.scope = block_scope

        for expr in node.expressions:
            self.visit(expr, block_scope.create_child())

    @visitor.when(nodes.VarDeclarationNode)
    def visit(self, node: nodes.VarDeclarationNode, scope: Scope):
        # I don't want to include the var before to avoid let a = a in print(a);
        self.visit(node.expr, scope.create_child())
        node.scope = scope.create_child()

        # Check if the variable type is a defined type, an error type or auto_type (we need to infer it)
        if node.var_type is not None:
            try:
                var_type = self.context.get_type_or_protocol(node.var_type)
            except HulkSemanticError as e:
                self.errors.append(e)
                var_type = ErrorType()
        else:
            var_type = AutoType()

        node.scope.define_variable(node.id, var_type)

    @visitor.when(nodes.LetInNode)
    def visit(self, node: nodes.LetInNode, scope: Scope):
        node.scope = scope
        # Create a new scope for every new variable declaration to follow scoping rules
        old_scope = scope
        for declaration in node.var_declarations:
            self.visit(declaration, old_scope)
            old_scope = declaration.scope

        self.visit(node.body, old_scope.create_child())
    
    @visitor.when(nodes.DestructiveAssignmentNode)
    def visit(self, node: nodes.DestructiveAssignmentNode, scope: Scope):
        node.scope = scope
        self.visit(node.id, scope.create_child())
        self.visit(node.expr, scope.create_child())

    @visitor.when(nodes.BinaryExpressionNode)
    def visit(self, node: nodes.BinaryExpressionNode, scope: Scope):
        node.scope = scope
        self.visit(node.left, scope.create_child())
        self.visit(node.right, scope.create_child())

    @visitor.when(nodes.UnaryExpressionNode)
    def visit(self, node: nodes.UnaryExpressionNode, scope: Scope):
        node.scope = scope
        self.visit(node.operand, scope.create_child())

    @visitor.when(nodes.ConditionalNode)
    def visit(self, node: nodes.ConditionalNode, scope: Scope):
        node.scope = scope
        if node.condition is not None:
            self.visit(node.condition, scope.create_child())

        self.visit(node.expression, scope.create_child())

        if node.else_expr is not None:
            self.visit(node.else_expr, scope.create_child())

    @visitor.when(nodes.WhileNode)
    def visit(self, node: nodes.WhileNode, scope: Scope):
        node.scope = scope
        self.visit(node.condition, scope.create_child())
        self.visit(node.expression, scope.create_child())

    @visitor.when(nodes.ForNode)
    def visit(self, node: nodes.ForNode, scope: Scope):
        node.scope = scope
        expr_scope = scope.create_child()

        expr_scope.define_variable(node.var, AutoType(), is_parameter=True)

        self.visit(node.iterable, scope.create_child())
        self.visit(node.expression, expr_scope)

    @visitor.when(nodes.IsNode)
    def visit(self, node: nodes.IsNode, scope: Scope):
        node.scope = scope
        self.visit(node.expression, scope.create_child())

    @visitor.when(nodes.AsNode)
    def visit(self, node: nodes.AsNode, scope: Scope):
        node.scope = scope
        self.visit(node.expression, scope.create_child())

    @visitor.when(nodes.FunctionCallNode)
    def visit(self, node: nodes.FunctionCallNode, scope: Scope):
        node.scope = scope
        for arg in node.args:
            self.visit(arg, scope.create_child())

    @visitor.when(nodes.BaseCallNode)
    def visit(self, node: nodes.BaseCallNode, scope: Scope):
        node.scope = scope
        for arg in node.args:
            self.visit(arg, scope.create_child())

    @visitor.when(nodes.AttributeCallNode)
    def visit(self, node: nodes.AttributeCallNode, scope: Scope):
        node.scope = scope
        self.visit(node.obj, scope.create_child())

    @visitor.when(nodes.MethodCallNode)
    def visit(self, node: nodes.MethodCallNode, scope: Scope):
        node.scope = scope
        self.visit(node.obj, scope.create_child())
        for arg in node.args:
            self.visit(arg, scope.create_child())

    @visitor.when(nodes.TypeInstantiationNode)
    def visit(self, node: nodes.TypeInstantiationNode, scope: Scope):
        node.scope = scope
        for arg in node.args:
            self.visit(arg, scope.create_child())

    @visitor.when(nodes.VectorInitializationNode)
    def visit(self, node: nodes.VectorInitializationNode, scope: Scope):
        node.scope = scope
        for element in node.elements:
            self.visit(element, scope.create_child())

    @visitor.when(nodes.VectorComprehensionNode)
    def visit(self, node: nodes.VectorComprehensionNode, scope: Scope):
        node.scope = scope

        selector_scope = scope.create_child()
        selector_scope.define_variable(node.var, AutoType(), is_parameter=True)
        self.visit(node.selector, selector_scope)

        self.visit(node.iterable, scope.create_child())

    @visitor.when(nodes.IndexingNode)
    def visit(self, node: nodes.IndexingNode, scope: Scope):
        node.scope = scope

        self.visit(node.obj, scope.create_child())
        self.visit(node.index, scope.create_child())

    @visitor.when(nodes.VariableNode)
    def visit(self, node: nodes.VariableNode, scope: Scope):
        node.scope = scope

    @visitor.when(nodes.ConstantBoolNode)
    def visit(self, node: nodes.ConstantBoolNode, scope: Scope):
        node.scope = scope

    @visitor.when(nodes.ConstantNumNode)
    def visit(self, node: nodes.ConstantNumNode, scope: Scope):
        node.scope = scope

    @visitor.when(nodes.ConstantStringNode)
    def visit(self, node: nodes.ConstantStringNode, scope: Scope):
        node.scope = scope