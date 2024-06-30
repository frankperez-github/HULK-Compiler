import Grammar.AST_nodes as nodes
import cmp.visitor as visitor
from errors import HulkSemanticError
from utils import Context
from types_ import ErrorType, AutoType

class TypeBuilder(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.errors: list = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(nodes.ProgramNode)
    def visit(self, node:nodes.ProgramNode):
        for declaration in node.declarations:
            self.visit(declaration)

    @visitor.when(nodes.FunctionDeclarationNode)
    def visit(self, node: nodes.FunctionDeclarationNode):
        params_names, params_types = self.get_params_names_and_types(node)

        if node.return_type is None:
            return_type = AutoType()
        else:
            try:
                # Check if the return type is declared
                return_type = self.context.get_type_or_protocol(node.return_type)
            except HulkSemanticError as e:
                self.errors.append(e)
                return_type = ErrorType()

        try:
            self.context.create_function(node.id, params_names, params_types, return_type, node)
        except HulkSemanticError as e:
            self.errors.append(e)

    def get_params_names_and_types(self, node):
        # For types that don't specify params
        if node.params_ids is None or node.params_types is None:
            return None, None

        params_names = []
        params_types = []

        for i, param_name in enumerate(node.params_ids):
            param_type = node.params_types[i]
            # Check if the parameter is already declared and set it to ErrorType
            if param_name in params_names:
                self.errors.append(HulkSemanticError(f'Parameter {param_name} is already declared'))
                index = params_names.index(param_name)
                params_types[index] = ErrorType()
            else:
                if param_type is None:
                    param_type = AutoType()
                else:
                    try:
                        param_type = self.context.get_type_or_protocol(param_type)
                    except HulkSemanticError as e:
                        self.errors.append(e)
                        param_type = ErrorType()
                params_types.append(param_type)
                params_names.append(param_name)

        return params_names, params_types

    @visitor.when(nodes.TypeDeclarationNode)
    def visit(self, node: nodes.TypeDeclarationNode):
        self.current_type = self.context.get_type(node.idx)

        if self.current_type.is_error():
            return

        self.current_type.params_names, self.current_type.params_types = self.get_params_names_and_types(node)

        # Check if the type is inheriting from a forbidden type
        if node.parent in ['Number', 'Boolean', 'String']:
            self.errors.append(HulkSemanticError(f'Type {node.idx} is inheriting from a forbidden type  -_-'))
        elif node.parent is not None:
            try:
                # Look for a circular dependency
                parent = self.context.get_type(node.parent)
                current = parent
                while current is not None:
                    if current.name == self.current_type.name:
                        self.errors.append(HulkSemanticError('Circular dependency inheritance  :O'))
                        parent = ErrorType()
                        break
                    current = current.parent
            except HulkSemanticError as e:
                # If the parent type is not declared, set it to ErrorType
                self.errors.append(e)
                parent = ErrorType()
            try:
                self.current_type.set_parent(parent)
            except HulkSemanticError as e:
                # If the parent type is already set
                self.errors.append(e)
        else:
            object_type = self.context.get_type('Object')
            self.current_type.set_parent(object_type)

        for attribute in node.attributes:
            self.visit(attribute)

        for method in node.methods:
            self.visit(method)

    @visitor.when(nodes.MethodDeclarationNode)
    def visit(self, node: nodes.MethodDeclarationNode):
        params_names, params_types = self.get_params_names_and_types(node)

        if node.return_type is None:
            return_type = AutoType()
        else:
            try:
                # Check if the return type is declared
                return_type = self.context.get_type_or_protocol(node.return_type)
            except HulkSemanticError as e:
                self.errors.append(e)
                return_type = ErrorType()

        try:
            self.current_type.define_method(node.id, params_names, params_types, return_type, node)
        except HulkSemanticError as e:

            self.errors.append(e)

    @visitor.when(nodes.AttributeDeclarationNode)
    def visit(self, node: nodes.AttributeDeclarationNode):
        # Set the attribute type to the declared type, ErrorType if it doesn't exist in the context or AutoType if we
        # are going to infer it
        if node.attribute_type is not None:
            try:
                attribute_type = self.context.get_type_or_protocol(node.attribute_type)
            except HulkSemanticError as e:
                self.errors.append(e)
                attribute_type = ErrorType()
        else:
            attribute_type = AutoType()

        try:
            self.current_type.define_attribute(node.id, attribute_type, node)
        except HulkSemanticError as e:
            self.errors.append(e)

    @visitor.when(nodes.ProtocolDeclarationNode)
    def visit(self, node: nodes.ProtocolDeclarationNode):
        self.current_type = self.context.get_protocol(node.idx)

        if self.current_type.is_error():
            return

        if node.parent is not None:
            try:
                # Look for a circular dependency
                parent = self.context.get_protocol(node.parent)
                current = parent
                while current is not None:
                    if current.name == self.current_type.name:
                        self.errors.append(HulkSemanticError('Circular dependency inheritance  :O'))
                        parent = ErrorType()
                        break
                    current = current.parent
            except HulkSemanticError as e:
                # If the parent type is not declared, set it to ErrorType
                self.errors.append(e)
                parent = ErrorType()
            try:
                self.current_type.set_parent(parent)
            except HulkSemanticError as e:
                # If the parent type is already set
                self.errors.append(e)

        for method in node.methods_signature:
            self.visit(method)

    @visitor.when(nodes.MethodSignatureDeclarationNode)
    def visit(self, node: nodes.MethodSignatureDeclarationNode):
        params_names, params_types = self.get_params_names_and_types(node)

        try:
            # Check if the return type is declared
            return_type = self.context.get_type_or_protocol(node.return_type)
        except HulkSemanticError as e:
            self.errors.append(e)
            return_type = ErrorType()

        try:
            self.current_type.define_method(node.id, params_names, params_types, return_type, node)
        except HulkSemanticError as e:
            self.errors.append(e)
