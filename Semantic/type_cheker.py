import Grammar.AST_nodes as nodes
import cmp.visitor as visitor
from errors import HulkSemanticError
from utils import Context, Scope, Function, VariableInfo
from types_ import ErrorType, AutoType, Method, SelfType, Type, Protocol, VectorType
from types_ import get_lowest_common_ancestor, get_most_specialized_type
from types_ import BoolType, NumberType



class TypeChecker(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.current_method = None
        self.errors= errors

    @visitor.on('node')
    def visit(self, node: nodes.Node):
        pass

    @visitor.when(nodes.ProgramNode)
    def visit(self, node: nodes.ProgramNode):
        for declaration in node.declarations:
            self.visit(declaration)

        self.visit(node.expression)

    
    @visitor.when(nodes.TypeDeclarationNode)
    def visit(self, node: nodes.TypeDeclarationNode):
        self.current_type = self.context.get_type(node.idx)

        if self.current_type.is_error():
            return

        for attr in node.attributes:
            self.visit(attr)

        for method in node.methods:
            self.visit(method)

        if self.current_type.parent.is_error():
            return

        parent_args_types = [self.visit(expr) for expr in node.parent_args]

        parent_params_types = self.current_type.parent.params_types

        if len(parent_args_types) != len(parent_params_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (
                len(parent_params_types), len(parent_args_types), self.current_type.parent.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        for parent_arg_type, parent_param_type in zip(parent_args_types, parent_params_types):
            if not parent_arg_type.conforms_to(parent_param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (parent_arg_type.name, parent_param_type.name)
                self.errors.append(HulkSemanticError(error_text))

        self.current_type = None

    @visitor.when(nodes.AttributeDeclarationNode)
    def visit(self, node: nodes.AttributeDeclarationNode):
        inf_type = self.visit(node.expr)

        attr_type = self.current_type.get_attribute(node.id).type

        if not inf_type.conforms_to(attr_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (inf_type.name, attr_type.name)
            self.errors.append(HulkSemanticError(error_text))

        return attr_type
    

    @visitor.when(nodes.MethodDeclarationNode)
    def visit(self, node: nodes.MethodDeclarationNode):
        self.current_method = self.current_type.get_method(node.id)

        inf_type = self.visit(node.expr)

        if not inf_type.conforms_to(self.current_method.return_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (inf_type.name, self.current_method.return_type.name)
            self.errors.append(HulkSemanticError(error_text))

        return_type = self.current_method.return_type

        # Check if override is correct
        if self.current_type.parent is None or self.current_type.parent.is_error():
            return return_type

        try:
            parent_method = self.current_type.parent.get_method(node.id)
        except HulkSemanticError:
            return return_type

        error_text = HulkSemanticError.WRONG_SIGNATURE % self.current_method.name

        if parent_method.return_type != return_type:
            self.errors.append(HulkSemanticError(error_text))
        elif len(parent_method.param_types) != len(self.current_method.param_types):
            self.errors.append(HulkSemanticError(error_text))
        else:
            for i, parent_param_type in enumerate(parent_method.param_types):
                param_type = self.current_method.param_types[i]
                if parent_param_type != param_type:
                    self.errors.append(HulkSemanticError(error_text))

        self.current_method = None

        return return_type

    
    @visitor.when(nodes.FunctionDeclarationNode)
    def visit(self, node: nodes.FunctionDeclarationNode):
        function: Function = self.context.get_function(node.id)

        inf_return_type = self.visit(node.expr)

        if not inf_return_type.conforms_to(function.return_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (inf_return_type.name, function.return_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return function.return_type

    @visitor.when(nodes.ExpressionBlockNode)
    def visit(self, node: nodes.ExpressionBlockNode):
        expr_type = ErrorType()

        for expr in node.expressions:
            expr_type = self.visit(expr)
        return expr_type

    
    @visitor.when(nodes.VarDeclarationNode)
    def visit(self, node: nodes.VarDeclarationNode):
        scope = node.scope

        inf_type = self.visit(node.expr)
        var_type = scope.find_variable(node.id).type

        if not inf_type.conforms_to(var_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (inf_type.name, var_type.name)
            self.errors.append(HulkSemanticError(error_text))
            var_type = ErrorType()

        return var_type

    @visitor.when(nodes.LetInNode)
    def visit(self, node: nodes.LetInNode):

        for declaration in node.var_declarations:
            self.visit(declaration)

        return self.visit(node.body)
    
    
    @visitor.when(nodes.DestructiveAssignmentNode)
    def visit(self, node: nodes.DestructiveAssignmentNode):
        new_type = self.visit(node.expr)
        old_type = self.visit(node.target)

        if old_type.name == 'Self':
            self.errors.append(HulkSemanticError(HulkSemanticError.SELF_IS_READONLY))
            return ErrorType()

        if not new_type.conforms_to(old_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (new_type.name, old_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return old_type
    
    
    @visitor.when(nodes.ConditionalNode)
    def visit(self, node: nodes.ConditionalNode):
        
        if node.condition is not None:
            cond_type = self.visit(node.condition)

            if cond_type != BoolType():
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (cond_type.name, BoolType().name)
                self.errors.append(HulkSemanticError(error_text))

        expr_type = self.visit(node.expression) 
        if node.else_expr is not None:
            else_type = self.visit(node.else_expr)
            return get_lowest_common_ancestor([expr_type] + [else_type])
        else:
            return expr_type
        
    
    @visitor.when(nodes.WhileNode)
    def visit(self, node: nodes.WhileNode):
        cond_type = self.visit(node.condition)

        if cond_type != BoolType():
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (cond_type.name, BoolType().name)
            self.errors.append(HulkSemanticError(error_text))

        return self.visit(node.expression)

    @visitor.when(nodes.ForNode)
    def visit(self, node: nodes.ForNode):
        ttype = self.visit(node.iterable)
        iterable_protocol = self.context.get_protocol('Iterable')

        if not ttype.conforms_to(iterable_protocol):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (ttype.name, iterable_protocol.name)
            self.errors.append(HulkSemanticError(error_text))

        return self.visit(node.expression)
    
    
    @visitor.when(nodes.FunctionCallNode)
    def visit(self, node: nodes.FunctionCallNode):
        args_types = [self.visit(arg) for arg in node.args]

        try:
            function = self.context.get_function(node.idx)
        except HulkSemanticError as e:
            self.errors.append(e)
            for arg in node.args:
                self.visit(arg)
            return ErrorType()

        if len(args_types) != len(function.param_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (
                len(function.param_types), len(args_types), function.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        for arg_type, param_type in zip(args_types, function.param_types):
            if not arg_type.conforms_to(param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(HulkSemanticError(error_text))
                return ErrorType()

        return function.return_type
    
    
    @visitor.when(nodes.MethodCallNode)
    def visit(self, node: nodes.MethodCallNode):
        args_types = [self.visit(arg) for arg in node.args]
        obj_type = self.visit(node.obj)

        if obj_type.is_error():
            return ErrorType()

        try:
            if obj_type == SelfType():
                method = self.current_type.get_method(node.method)
            else:
                method = obj_type.get_method(node.method)
        except HulkSemanticError as e:
            self.errors.append(e)
            for arg in node.args:
                self.visit(arg)
            return ErrorType()

        if len(args_types) != len(method.param_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (len(method.param_types), len(args_types), method.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        for arg_type, param_type in zip(args_types, method.param_types):
            if not arg_type.conforms_to(param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(HulkSemanticError(error_text))
                return ErrorType()

        return method.return_type
    
    
    @visitor.when(nodes.BaseCallNode)
    def visit(self, node: nodes.BaseCallNode):
        if self.current_method is None:
            self.errors.append(HulkSemanticError(HulkSemanticError.BASE_OUTSIDE_METHOD))
            for arg in node.args:
                self.visit(arg)
            return ErrorType()

        try:
            method = self.current_type.parent.get_method(self.current_method.name)
            node.method_name = self.current_method.name
            node.parent_type = self.current_type.parent
        except HulkSemanticError:
            error_text = HulkSemanticError.METHOD_NOT_DEFINED % self.current_method.name
            self.errors.append(HulkSemanticError(error_text))
            for arg in node.args:
                self.visit(arg)
            return ErrorType()

        args_types = [self.visit(arg) for arg in node.args]

        if len(args_types) != len(method.param_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (len(method.param_types), len(args_types), method.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        for arg_type, param_type in zip(args_types, method.param_types):
            if not arg_type.conforms_to(param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(HulkSemanticError(error_text))
                return ErrorType()

        return method.return_type
    
    
    @visitor.when(nodes.AttributeCallNode)
    def visit(self, node: nodes.AttributeCallNode):
        obj_type = self.visit(node.obj)

        if obj_type.is_error():
            return ErrorType()

        if obj_type == SelfType():
            try:
                attr = self.current_type.get_attribute(node.attribute)
                return attr.type
            except HulkSemanticError as e:
                self.errors.append(e)
                return ErrorType()
        else:
            self.errors.append(HulkSemanticError("Cannot access an attribute from a non-self object"))
            return ErrorType()
        
    
    @visitor.when(nodes.IsNode)
    def visit(self, node: nodes.IsNode):
        self.visit(node.expression)
        bool_type = self.context.get_type('Boolean')

        try:
            self.context.get_type_or_protocol(node.ttype)
        except HulkSemanticError as e:
            self.errors.append(e)

        return bool_type
    
    
    @visitor.when(nodes.AsNode)
    def visit(self, node: nodes.AsNode):
        expression_type = self.visit(node.expression)

        try:
            cast_type = self.context.get_type_or_protocol(node.ttype)
        except HulkSemanticError as e:
            self.errors.append(e)
            cast_type = ErrorType()

        if not expression_type.conforms_to(cast_type) and not cast_type.conforms_to(expression_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (expression_type.name, cast_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return cast_type
    
    
    @visitor.when(nodes.ArithmeticExpressionNode)
    def visit(self, node: nodes.ArithmeticExpressionNode):
        number_type = self.context.get_type('Number')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type == NumberType() or not right_type == NumberType():
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return number_type

    @visitor.when(nodes.InequalityExpressionNode)
    def visit(self, node: nodes.ArithmeticExpressionNode):
        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type == NumberType() or not right_type == NumberType():
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return bool_type

    @visitor.when(nodes.BoolBinaryExpressionNode)
    def visit(self, node: nodes.BoolBinaryExpressionNode):
        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type == BoolType() or not right_type == BoolType():
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return bool_type

    @visitor.when(nodes.StringBinaryExpressionNode)
    def visit(self, node: nodes.StringBinaryExpressionNode):
        string_type = self.context.get_type('String')
        object_type = self.context.get_type('Object')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type.conforms_to(object_type) or not right_type.conforms_to(object_type):
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return string_type
    
    
    @visitor.when(nodes.EqualityExpressionNode)
    def visit(self, node: nodes.ArithmeticExpressionNode):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type.conforms_to(right_type) and not right_type.conforms_to(left_type):
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return self.context.get_type('Boolean')

    
    @visitor.when(nodes.NegNode)
    def visit(self, node: nodes.NegNode):
        operand_type = self.visit(node.operand)
        number_type = self.context.get_type('Number')

        if operand_type != NumberType():
            error_text = HulkSemanticError.INVALID_UNARY_OPERATION % (node.operator, operand_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return number_type

        return number_type
    
    
    @visitor.when(nodes.NotNode)
    def visit(self, node: nodes.NotNode):
        operand_type = self.visit(node.operand)
        bool_type = self.context.get_type('Boolean')

        if operand_type != BoolType():
            error_text = HulkSemanticError.INVALID_UNARY_OPERATION % (node.operator, operand_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return bool_type

    @visitor.when(nodes.ConstantBoolNode)
    def visit(self, node: nodes.ConstantBoolNode):
        return self.context.get_type('Boolean')

    @visitor.when(nodes.ConstantNumNode)
    def visit(self, node: nodes.ConstantNumNode):
        return self.context.get_type('Number')

    @visitor.when(nodes.ConstantStringNode)
    def visit(self, node: nodes.ConstantStringNode):
        return self.context.get_type('String')
    
    
    @visitor.when(nodes.VariableNode)
    def visit(self, node: nodes.VariableNode):
        scope = node.scope

        if not scope.is_defined(node.lex):
            error_text = HulkSemanticError.VARIABLE_NOT_DEFINED % node.lex
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        var = scope.find_variable(node.lex)
        return var.type

    
    @visitor.when(nodes.TypeInstantiationNode)
    def visit(self, node: nodes.TypeInstantiationNode):
        try:
            ttype = self.context.get_type(node.idx, params_len=len(node.args))
        except HulkSemanticError as e:
            self.errors.append(e)
            return ErrorType()

        args_types = [self.visit(arg) for arg in node.args]

        if len(args_types) != len(ttype.params_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (len(ttype.params_types), len(args_types), ttype.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        for arg_type, param_type in zip(args_types, ttype.params_types):
            if not arg_type.conforms_to(param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(HulkSemanticError(error_text))
                return ErrorType()

        return ttype


    @visitor.when(nodes.VectorInitializationNode)
    def visit(self, node: nodes.VectorInitializationNode):
        elements_types = [self.visit(element) for element in node.elements]
        lca = get_lowest_common_ancestor(elements_types)

        if lca.is_error():
            return ErrorType()

        return VectorType(lca)
    
    
    @visitor.when(nodes.VectorComprehensionNode)
    def visit(self, node: nodes.VectorComprehensionNode):
        ttype = self.visit(node.iterable)
        iterable_protocol = self.context.get_protocol('Iterable')

        return_type = self.visit(node.selector)

        if not ttype.conforms_to(iterable_protocol):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (ttype.name, iterable_protocol.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        if return_type.is_error():
            return ErrorType()

        return VectorType(return_type)
    
    
    @visitor.when(nodes.IndexingNode)
    def visit(self, node: nodes.IndexingNode):
        number_type = self.context.get_type('Number')

        index_type = self.visit(node.index)
        if index_type != number_type:
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (index_type.name, number_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        obj_type = self.visit(node.obj)

        if obj_type.is_error():
            return ErrorType()

        if not isinstance(obj_type, VectorType):
            error_text = HulkSemanticError.INVALID_UNARY_OPERATION % ('[]', obj_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return ErrorType()

        return obj_type.get_element_type()


    @visitor.when(nodes.ProtocolDeclarationNode)
    def visit(self, node: nodes.ProtocolDeclarationNode):
        self.current_type = self.context.get_protocol(node.idx)
        for method in node.methods_signature:
            self.visit(method)
        self.current_type = None
    
    
    @visitor.when(nodes.MethodSignatureDeclarationNode)
    def visit(self, node: nodes.MethodSignatureDeclarationNode):
        if self.current_type.is_error():
            return ErrorType()

        self.current_method = self.current_type.get_method(node.id)
        return  self.current_method.return_type