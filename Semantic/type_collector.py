import Grammar.AST_nodes as nodes
import cmp.visitor as visitor
from errors import HulkSemanticError
from utils import Context

class TypeCollector(object):

    def __init__(self, errors) -> None:
        self.context = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(nodes.ProgramNode)
    def visit(self, node:nodes.ProgramNode):
        # Create the global context
        self.context = Context()

        # Add the basic types
        object_type = self.context.create_type('Object')

        number_type = self.context.create_type('Number')
        number_type.set_parent(object_type)

        bool_type = self.context.create_type('Boolean')
        bool_type.set_parent(object_type)

        string_type = self.context.create_type('String')
        string_type.set_parent(object_type)
        string_type.define_method('size', [], [], number_type)
        string_type.define_method('next', [], [], bool_type)
        string_type.define_method('current', [], [], string_type)

        object_type.define_method('equals', ['other'], [object_type], bool_type)
        object_type.define_method('toString', [], [], string_type)

        # Add the built-in functions
        self.context.create_function('print', ['value'], [object_type], string_type)
        self.context.create_function('sqrt', ['value'], [number_type], number_type)
        self.context.create_function('sin', ['angle'], [number_type], number_type)
        self.context.create_function('cos', ['angle'], [number_type], number_type)
        self.context.create_function('exp', ['value'], [number_type], number_type)
        self.context.create_function('log', ['value'], [number_type], number_type)
        self.context.create_function('rand', [], [], number_type)
        self.context.create_function('parse', ['value'], [string_type], number_type)

        # Add iterable protocol
        iterable_protocol = self.context.create_protocol('Iterable')
        iterable_protocol.define_method('next', [], [], bool_type)
        iterable_protocol.define_method('current', [], [], object_type)

        range_type = self.context.create_type('Range')
        range_type.set_parent(object_type)
        range_type.params_names, range_type.params_types = ['min', 'max'], [number_type, number_type]
        range_type.define_attribute('min', number_type)
        range_type.define_attribute('max', number_type)
        range_type.define_attribute('current', number_type)
        range_type.define_method('next', [], [], bool_type)
        range_type.define_method('current', [], [], number_type)

        self.context.create_function('range', ['min', 'max'], [number_type, number_type], range_type)

        for decl in node.declarations:
            self.visit(decl)
        return self.context, self.errors

    @visitor.when(nodes.TypeDeclarationNode)
    def visit(self, node:nodes.TypeDeclarationNode):
        try:
            self.context.create_type(node.idx, node)
        except HulkSemanticError as e:
            self.errors.append(e)
            self.context.set_type_or_protocol_error(node.idx)

    @visitor.when(nodes.ProtocolDeclarationNode)
    def visit(self, node: nodes.ProtocolDeclarationNode):
        try:
            self.context.create_protocol(node.idx, node)
        except HulkSemanticError as e:
            self.errors.append(e)
            self.context.set_type_or_protocol_error(node.idx)

