import Grammar.AST_nodes as nodes
import cmp.visitor as visitor
from errors import HulkSemanticError
from Semantic.utils import Context, Scope, Function
from Semantic.types_ import ErrorType, AutoType, SelfType, Type, Protocol, VectorType
from Semantic.types_ import get_lowest_common_ancestor, get_most_specialized_type


class TypeInferrer(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.current_method = None
        self.errors= errors
        self.had_changed = False
        self.c=0

    def assign_auto_type(self, node:nodes.Node, scope: Scope, inf_type: Type | Protocol):
        """
        Agrega el tipo inferido a una variable en el scope
        :param node: El nodo que fue inferido
        :param scope: Scope de la variable
        :param inf_type: Tipo inferido
        """
        if isinstance(node, nodes.VariableNode) and scope.is_defined(node.lex):
            var_info = scope.find_variable(node.lex)
            if var_info.type != AutoType() or var_info.type.is_error():
                return
            var_info.inferred_types.append(inf_type)
            if not isinstance(inf_type, AutoType):
                self.had_changed = True
        if isinstance(node, nodes.IndexingNode):
            self.assign_auto_type(node.obj, scope, VectorType(inf_type))

        if isinstance(node, nodes.AttributeCallNode):
            
            if(node.obj.lex=='self'):
                try:
                    attr = self.current_type.get_attribute(node.attribute)
                    if(isinstance(attr.type,AutoType)):
                        attr.type=inf_type
                    return
                except HulkSemanticError:
                    return 
            else:
                try:
                    attr = self.context.get_type(node.obj.lex).get_attribute(node.attribute)
                    if(isinstance(attr.type,AutoType)):
                        attr.type=inf_type
                    return
                except HulkSemanticError:
                    return 

            

    @visitor.on('node')
    def visit(self, node: nodes.Node):
        pass

    @visitor.when(nodes.ProgramNode)
    def visit(self, node: nodes.ProgramNode):

        for declaration in node.declarations:
            self.visit(declaration)

        self.visit(node.expression)

        if self.had_changed and self.c <500:
            self.had_changed = False
            self.c+=1
            self.visit(node)

    @visitor.when(nodes.TypeDeclarationNode)
    def visit(self, node: nodes.TypeDeclarationNode):
        self.current_type = self.context.get_type(node.id)
        if self.current_type.is_error():
            return

        const_scope = node.scope.children[0]

        args_types = [self.visit(arg) for arg in node.parent_args]

        if not self.current_type.parent.is_error():
            for arg, param_type in zip(node.parent_args, self.current_type.parent.params_types):
                self.assign_auto_type(arg, arg.scope, param_type)

            for i, param_type in enumerate(self.current_type.parent.params_types):
                if len(args_types) <= i:
                    break
                arg = args_types[i]
                if param_type == AutoType() and not param_type.is_error():
                    var = self.current_type.parent.param_vars[i]
                    var.inferred_types.append(arg)
                    self.had_changed = True

        for attr in node.attributes:
            self.visit(attr)

        # Comprobar si podemos inferir el tipo de algunos parametros
        for i, param_type in enumerate(self.current_type.params_types):
            param_name = self.current_type.params_names[i]
            local_var = const_scope.find_variable(param_name)
            local_var.type = param_type
            # Comprobar si podemos inferir el tipo del parametro en el cuerpo
            if isinstance(param_type, AutoType) and local_var.is_parameter and local_var.inferred_types:
                try:
                    new_type = get_most_specialized_type(local_var.inferred_types, var_name=param_name)
                except HulkSemanticError as e:
                    self.errors.append(e)
                    new_type = ErrorType()
                self.current_type.params_types[i] = new_type
                if not isinstance(new_type, AutoType):
                    self.had_changed = True
                local_var.set_type_and_clear_inference_types_list(new_type)
            # Comprobar si podemos inferir el tipo del parametro por algun llamado
            if (isinstance(self.current_type.params_types[i], AutoType)
                    and self.current_type.param_vars[i].inferred_types):
                new_type = get_lowest_common_ancestor(self.current_type.param_vars[i].inferred_types)
                self.current_type.params_types[i] = new_type
                if not isinstance(new_type, AutoType):
                    self.had_changed = True
                local_var.set_type_and_clear_inference_types_list(new_type)

            # Inferir el tipo de retorno y el tipo de los parametros de los metodos
        for method in node.methods:
            self.visit(method)

        for attr in node.attributes:
            if (isinstance(attr.expr,nodes.VariableNode) and not isinstance(self.current_type.get_attribute(attr.id).type,AutoType)):
                param_var=const_scope.find_variable(attr.expr.lex)
                if(param_var is not None):
                        param_var.inferred_types.append(self.current_type.get_attribute(attr.id).type)
                 
        self.current_type = None

    @visitor.when(nodes.AttributeDeclarationNode)
    def visit(self, node: nodes.AttributeDeclarationNode):
        inf_type = self.visit(node.expr)

        attribute = self.current_type.get_attribute(node.id)
        if attribute.type.is_error():
            attr_type = ErrorType()
        elif attribute.type != AutoType():
            attr_type = attribute.type
        else:
            attr_type = inf_type

        attribute.type = attr_type
        return attr_type


    @visitor.when(nodes.FunctionDeclarationNode)
    def visit(self, node: nodes.FunctionDeclarationNode):
        function: Function = self.context.get_function(node.id)

        return_type = self.visit(node.expr)

        if function.return_type == AutoType() and not function.return_type.is_error() and (
                return_type != AutoType() or return_type.is_error()):
            self.had_changed = True
            function.return_type = return_type

        expr_scope = node.expr.scope

        # Comprobar si podemos inferir el tipo de algunos parametros
        for i, param_type in enumerate(function.param_types):
            param_name = function.param_names[i]
            local_var = expr_scope.find_variable(param_name)
            local_var.type = param_type
            # Comprobar si podemos inferir el tipo del parametro en el cuerpo
            if isinstance(param_type, AutoType) and local_var.is_parameter and local_var.inferred_types:
                try:
                    new_type = get_most_specialized_type(local_var.inferred_types, var_name=param_name)
                except HulkSemanticError as e:
                    self.errors.append(e)
                    new_type = ErrorType()
                function.param_types[i] = new_type
                if not isinstance(new_type, AutoType):
                    self.had_changed = True
                local_var.set_type_and_clear_inference_types_list(new_type)
            # Comprobar si podemos inferir el tipo del parametro por algun llamado
            if isinstance(function.param_types[i], AutoType) and function.param_vars[i].inferred_types:
                new_type = get_lowest_common_ancestor(function.param_vars[i].inferred_types)
                function.param_types[i] = new_type
                if not isinstance(new_type, AutoType):
                    self.had_changed = True
                local_var.set_type_and_clear_inference_types_list(new_type)

        return return_type



    @visitor.when(nodes.MethodDeclarationNode)
    def visit(self, node: nodes.MethodDeclarationNode):
        self.current_method = self.current_type.get_method(node.id)

        method_scope = node.expr.scope
        return_type = self.visit(node.expr)

        if self.current_method.return_type == AutoType() and not self.current_method.return_type.is_error() and (
                return_type != AutoType() or return_type.is_error()):
            self.had_changed = True
            self.current_method.return_type = return_type

        # Comprobar si podemos inferir el tipo de algunos parametros
        for i, param_type in enumerate(self.current_method.param_types):
            param_name = self.current_method.param_names[i]
            local_var = method_scope.find_variable(param_name)
            local_var.type = param_type
            # Comprobar si podemos inferir el tipo del parametro en el cuerpo
            if isinstance(param_type,AutoType) and local_var.is_parameter and local_var.inferred_types:
                try:
                    new_type = get_most_specialized_type(local_var.inferred_types, var_name=param_name)
                except HulkSemanticError as e:
                    self.errors.append(e)
                    new_type = ErrorType()
                self.current_method.param_types[i] = new_type
                if not isinstance(new_type, AutoType):
                    self.had_changed = True
                local_var.set_type_and_clear_inference_types_list(new_type)
            # Comprobar si podemos inferir el tipo del parametro por algun llamado
            if (isinstance(self.current_method.param_types[i],AutoType)
                    and self.current_method.param_vars[i].inferred_types):
                new_type = get_lowest_common_ancestor(self.current_method.param_vars[i].inferred_types)
                self.current_method.param_types[i] = new_type
                if not isinstance(new_type, AutoType):
                    self.had_changed = True
                local_var.set_type_and_clear_inference_types_list(new_type)
        self.current_method = None

        return return_type


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
        var = scope.find_variable(node.id)
        var.type = var.type if var.type != AutoType() or var.type.is_error() else inf_type
        return var.type
    
    @visitor.when(nodes.LetInNode)
    def visit(self, node: nodes.LetInNode):
        for declaration in node.var_declarations:
            self.visit(declaration)
        return self.visit(node.body)
    
    @visitor.when(nodes.DestructiveAssignmentNode)
    def visit(self, node: nodes.DestructiveAssignmentNode):
        new_type = self.visit(node.expr)
        old_type = self.visit(node.id)

        if old_type.name == 'Self':
            return ErrorType()


        if(isinstance(node.id,nodes.AttributeCallNode) and isinstance(old_type,AutoType) and not isinstance(new_type,AutoType)):
            self.assign_auto_type(node.id, node.scope, new_type)


        if isinstance(new_type, AutoType) and not isinstance(old_type, AutoType):
            self.assign_auto_type(node.expr, node.scope, old_type)

        return old_type

    @visitor.when(nodes.ConditionalNode)
    def visit(self, node: nodes.ConditionalNode):
        if node.condition is not None:
            self.visit(node.condition)

        expr_type = self.visit(node.expression) 

        if node.else_expr is not None:
            else_type = self.visit(node.else_expr)
            return get_lowest_common_ancestor([expr_type] + [else_type])
        else:
            return expr_type

    @visitor.when(nodes.WhileNode)
    def visit(self, node: nodes.WhileNode):
        self.visit(node.condition)
        return self.visit(node.expression)
    

    @visitor.when(nodes.ForNode)
    def visit(self, node: nodes.ForNode):
        iterable_protocol = self.context.get_protocol('Iterable')
        ttype = self.visit(node.iterable)

        expr_scope = node.expression.scope
        variable = expr_scope.find_variable(node.var)

        # Comprobar si podemos inferir el tipo del iterable
        if ttype.is_error():
            variable.type = ErrorType()
        elif ttype == AutoType():
            variable.type = AutoType()
        elif ttype.conforms_to(iterable_protocol):
            element_type = ttype.get_method('current').return_type
            variable.type = element_type
        else:
            variable.type = ErrorType()

        expr_type = self.visit(node.expression)
        return expr_type
    
    @visitor.when(nodes.FunctionCallNode)
    def visit(self, node: nodes.FunctionCallNode):
        scope = node.scope

        args_types = [self.visit(arg) for arg in node.args]

        try:
            function = self.context.get_function(node.id)
        except HulkSemanticError:
            return ErrorType()

        for arg, param_type in zip(node.args, function.param_types):
            self.assign_auto_type(arg, scope, param_type)

        for i, func_param_type in enumerate(function.param_types):
            if len(args_types) <= i:
                break
            arg = args_types[i]
            if func_param_type == AutoType() and not func_param_type.is_error():
                var = function.param_vars[i]
                var.inferred_types.append(arg)
                self.had_changed = True
    
        return function.return_type
    
    @visitor.when(nodes.BaseCallNode)
    def visit(self, node: nodes.BaseCallNode):
        scope = node.scope

        if self.current_method is None:
            return ErrorType()

        args_types = [self.visit(arg) for arg in node.args]

        try:
            method = self.current_type.parent.get_method(self.current_method.name)
        except HulkSemanticError:
            for arg in node.args:
                self.visit(arg)
            return ErrorType()

        for arg, param_type in zip(node.args, method.param_types):
            self.assign_auto_type(arg, scope, param_type)

        for i, func_param_type in enumerate(method.param_types):
            if len(args_types) <= i:
                break
            arg_type = args_types[i]
            if func_param_type == AutoType() and not func_param_type.is_error():
                var = method.param_vars[i]
                var.inferred_types.append(arg_type)
                self.had_changed = True

        return method.return_type
    
    @visitor.when(nodes.MethodCallNode)
    def visit(self, node: nodes.MethodCallNode):
        scope = node.scope
        obj_type = self.visit(node.obj)

        if obj_type.is_error():
            return ErrorType()

        args_types = [self.visit(arg) for arg in node.args]

        try:
            if obj_type == SelfType():
                method = self.current_type.get_method(node.method)
            else:
                method = obj_type.get_method(node.method)
        except HulkSemanticError:
            return ErrorType()

        for arg, param_type in zip(node.args, method.param_types):
            self.assign_auto_type(arg, scope, param_type)

        for i, method_param_type in enumerate(method.param_types):
            if len(args_types) <= i:
                break
            arg = args_types[i]
            if method_param_type == AutoType() and not method_param_type.is_error():
                var = method.param_vars[i]
                var.inferred_types.append(arg)
                self.had_changed = True

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
            except HulkSemanticError:
                return ErrorType()
        else:
            # Can't access to a non-self attribute
            return ErrorType()
        
    
    @visitor.when(nodes.IsNode)
    def visit(self, node: nodes.IsNode):
        bool_type = self.context.get_type('Boolean')
        self.visit(node.expression)
        return bool_type
    
    @visitor.when(nodes.AsNode)
    def visit(self, node: nodes.AsNode):
        expr_type = self.visit(node.expression)

        try:
            cast_type = self.context.get_type_or_protocol(node.type)
        except HulkSemanticError:
            cast_type = ErrorType()

        if expr_type == AutoType() and not expr_type.is_error():
            return cast_type

        return cast_type
    
    @visitor.when(nodes.ArithmeticExpressionNode)
    def visit(self, node: nodes.ArithmeticExpressionNode):
        scope = node.scope

        number_type = self.context.get_type('Number')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == AutoType() and not left_type.is_error():
            self.assign_auto_type(node.left, scope, number_type)
        elif left_type != number_type or left_type.is_error():
            return ErrorType()

        if right_type == AutoType() and not right_type.is_error():
            self.assign_auto_type(node.right, scope, number_type)
        elif right_type != number_type or right_type.is_error():
            return ErrorType()

        return number_type
    
    @visitor.when(nodes.InequalityExpressionNode)
    def visit(self, node: nodes.ArithmeticExpressionNode):
        scope = node.scope
        bool_type = self.context.get_type('Boolean')
        number_type = self.context.get_type('Number')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == AutoType() and not left_type.is_error():
            self.assign_auto_type(node.left, scope, number_type)
        elif left_type != number_type or left_type.is_error():
            return ErrorType()

        if right_type == AutoType() and not right_type.is_error():
            self.assign_auto_type(node.right, scope, number_type)
        elif right_type != number_type or right_type.is_error():
            return ErrorType()

        return bool_type
    
    @visitor.when(nodes.BoolBinaryExpressionNode)
    def visit(self, node: nodes.BoolBinaryExpressionNode):
        scope = node.scope

        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == AutoType() and not left_type.is_error():
            self.assign_auto_type(node.left, scope, bool_type)
        elif left_type != bool_type or left_type.is_error():
            return ErrorType()

        if right_type == AutoType() and not right_type.is_error():
            self.assign_auto_type(node.right, scope, bool_type)
        elif right_type != bool_type or right_type.is_error():
            return ErrorType()

        return bool_type
    
    @visitor.when(nodes.StringBinaryExpressionNode)
    def visit(self, node: nodes.StringBinaryExpressionNode):
        scope = node.scope

        string_type = self.context.get_type('String')
        object_type = self.context.get_type('Object')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == AutoType() and not left_type.is_error():
            self.assign_auto_type(node.left, scope, object_type)
        elif left_type.is_error():
            return ErrorType()

        if right_type == AutoType() and not right_type.is_error():
            self.assign_auto_type(node.right, scope, object_type)
        elif right_type.is_error():
            return ErrorType()

        return string_type
    
    @visitor.when(nodes.EqualityExpressionNode)
    def visit(self, node: nodes.EqualityExpressionNode):
        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if (left_type == AutoType() and not left_type.is_error()) or (
                right_type == AutoType() and not right_type.is_error()):
            return bool_type

        return bool_type
    
    @visitor.when(nodes.NegNode)
    def visit(self, node: nodes.NegNode):
        scope = node.scope

        operand_type = self.visit(node.operand)
        number_type = self.context.get_type('Number')

        if operand_type == AutoType():
            self.assign_auto_type(node.operand, scope, number_type)
        elif operand_type != number_type or operand_type.is_error():
            return ErrorType()

        return number_type
    
    
    @visitor.when(nodes.NotNode)
    def visit(self, node: nodes.NotNode):
        scope = node.scope

        operand_type = self.visit(node.operand)
        bool_type = self.context.get_type('Boolean')

        if operand_type == AutoType() and not operand_type.is_error():
            self.assign_auto_type(node.operand, scope, bool_type)
        elif operand_type != bool_type or operand_type.is_error():
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
            return ErrorType()

        var = scope.find_variable(node.lex)
        return var.type

    @visitor.when(nodes.TypeInstantiationNode)
    def visit(self, node: nodes.TypeInstantiationNode):
        args_types = [self.visit(arg) for arg in node.args]

        try:
            ttype = self.context.get_type(node.id)
        except HulkSemanticError:
            for arg in node.args:
                self.visit(arg)
            return ErrorType()

        if ttype.is_error():
            return ErrorType()

        for arg, param_type in zip(node.args, ttype.params_types):
            self.assign_auto_type(arg, node.scope, param_type)

        for i, param_type in enumerate(ttype.params_types):
            if len(args_types) <= i:
                break
            arg = args_types[i]
            if param_type == AutoType() and not param_type.is_error():
                var = ttype.param_vars[i]
                var.inferred_types.append(arg)
                self.had_changed = True

        return ttype


    @visitor.when(nodes.VectorInitializationNode)
    def visit(self, node: nodes.VectorInitializationNode):
        elements_types = [self.visit(element) for element in node.elements]
        lca = get_lowest_common_ancestor(elements_types)

        if lca.is_error():
            return ErrorType()
        elif lca == AutoType():
            return AutoType()

        return VectorType(lca)
    
    @visitor.when(nodes.VectorComprehensionNode)
    def visit(self, node: nodes.VectorComprehensionNode):
        ttype = self.visit(node.iterable)
        iterable_protocol = self.context.get_protocol('Iterable')

        selector_scope = node.function.scope

        variable = selector_scope.find_variable(node.var)

        if ttype.is_error():
            variable.type = ErrorType()
        elif ttype == AutoType():
            variable.type = AutoType()
        elif ttype.conforms_to(iterable_protocol):
            element_type = ttype.get_method('current').return_type
            variable.type = element_type
        else:
            variable.type =ErrorType()

        return_type = self.visit(node.function)

        if return_type.is_error():
            return ErrorType()
        elif return_type == AutoType():
            return AutoType()

        return VectorType(return_type)
    
    
    @visitor.when(nodes.IndexingNode)
    def visit(self, node: nodes.IndexingNode):
        scope = node.scope

        number_type = self.context.get_type('Number')

        index_type = self.visit(node.index)
        obj_type = self.visit(node.obj)

        if index_type == AutoType() and not index_type.is_error():
            self.assign_auto_type(node.index, scope, number_type)
        elif index_type != number_type or index_type.is_error():
            return ErrorType()

        if obj_type.is_error():
            return ErrorType()
        elif obj_type == AutoType():
            return AutoType()

        if not isinstance(obj_type, VectorType):
            return ErrorType()

        return obj_type.get_element_type()