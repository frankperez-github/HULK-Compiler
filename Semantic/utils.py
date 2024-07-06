from errors import HulkSemanticError
from Semantic.types_ import Type, Protocol, AutoType, ErrorType, VectorType
import Grammar.AST_nodes
import itertools as itt

class Function:
    def __init__(self, name, param_names, param_types, return_type, node=None):
        self.name = name
        self.node = node
        self.param_names = param_names
        self.param_types = param_types
        self.param_vars = []
        self.return_type = return_type

    
    def inference_errors(self):
        errors = []

        for i, param_type in enumerate(self.param_types):
            if isinstance(param_type, AutoType):
                param_name = self.param_names[i]
                error_message = HulkSemanticError.CANNOT_INFER_PARAM_TYPE % (param_name, self.name)
                errors.append(HulkSemanticError(error_message))
                self.param_types[i] = ErrorType()

        if self.return_type == AutoType() and not self.return_type.is_error():
            errors.append(HulkSemanticError(HulkSemanticError.CANNOT_INFER_RETURN_TYPE % self.name))
            self.return_type = ErrorType()
        return errors

    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n, t in zip(self.param_names, self.param_types))
        return '\n' + f'function {self.name}({params}): {self.return_type.name};' + '\n'

    def __eq__(self, other):
        return other.name == self.name and \
            other.return_type == self.return_type and \
            other.param_types == self.param_types
    

class Context:
    def __init__(self):
        self.types = {}
        self.protocols = {}
        self.functions = {}

    def create_type(self, name: str, node=None) -> Type:
        if name in self.types:
            raise HulkSemanticError(f'Type with the same name ({name}) already in context.')
        if name in self.protocols:
            raise HulkSemanticError(f'Protocol with the same name ({name}) already in context.')
        typex = self.types[name] = Type(name, node)
        return typex

    def get_type(self, name, params_len=None) -> Type:
        try:
            ttype: Type = self.types[name]
            if ttype.is_error() and params_len:
                ttype = ErrorType()
                ttype.params_names = ['<error>'] * params_len
                ttype.params_types = [ErrorType()] * params_len
            return ttype
        except KeyError:
            raise HulkSemanticError(f'Type "{name}" is not defined.')

    def create_protocol(self, name: str, node=None) -> Protocol:
        if name in self.protocols:
            raise HulkSemanticError(f'Protocol with the same name ({name}) already in context.')
        if name in self.types:
            raise HulkSemanticError(f'Type with the same name ({name}) already in context.')
        protocol = self.protocols[name] = Protocol(name, node)
        return protocol

    def get_protocol(self, ttype) -> Protocol:
        try:
            return self.protocols[ttype]
        except KeyError:
            raise HulkSemanticError(f'Protocol "{ttype}" is not defined.')

    def get_type_or_protocol(self, ttype):
        if isinstance(ttype, Grammar.AST_nodes.VectorTypeAnnotationNode):
            element_type = self.get_type_or_protocol(ttype.element_type)
            return VectorType(element_type)
        else:
            try:
                return self.get_protocol(ttype)
            except HulkSemanticError:
                return self.get_type(ttype)

    def set_type_or_protocol_error(self, name):
        if name in self.types:
            self.types[name] = ErrorType()
        elif name in self.protocols:
            self.protocols[name] = ErrorType()
        else:
            raise HulkSemanticError(f'Type or protocol "{name}" is not defined.')

    def create_function(self, name: str, params_names: list, params_types: list, return_type, node=None) -> Function:
        if name in self.functions:
            raise HulkSemanticError(f'Function with the same name ({name}) already in context.')
        function = self.functions[name] = Function(name, params_names, params_types, return_type, node)
        return function

    def get_function(self, name: str) -> Function:
        try:
            return self.functions[name]
        except KeyError:
            raise HulkSemanticError(f'Function "{name}" is not defined.')

    
    def inference_errors(self):
        errors = []
        for type_name in self.types:
            errors.extend(self.types[type_name].inference_errors())
        for func_name in self.functions:
            errors.extend(self.functions[func_name].inference_errors())
        return errors

    def __str__(self):
        return ('{\n\t' +
                '\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) +
                '\n\t'.join(y for x in self.protocols.values() for y in str(x).split('\n')) +
                '\n\t'.join(y for x in self.functions.values() for y in str(x).split('\n')) +
                '\n}')

    def __repr__(self):
        return str(self)


class VariableInfo:
    def __init__(self, name, vtype, is_parameter=False):
        self.name = name
        self.type = vtype
        self.inferred_types = []
        self.is_parameter = is_parameter
        self.nameC = None

    def setNameC(self, name: str):
        self.nameC = name

    
    def set_type_and_clear_inference_types_list(self, ttype: Type | Protocol):
        self.type = ttype
        self.inferred_types = []

    
    def inference_errors(self):
        # If the variable is a parameter, we don't need to report errors because it was already reported
        if self.type == AutoType() and self.is_parameter:
            self.type = ErrorType()
            return []

        errors = []
        if self.type == AutoType() and not self.type.is_error():
            self.type = ErrorType()
            errors.append(HulkSemanticError(HulkSemanticError.CANNOT_INFER_VAR_TYPE % self.name))

        return errors

    def __str__(self):
        return f'{self.name} : {self.type.name} inf:{[inf.name for inf in self.inferred_types]}'

    def __repr__(self):
        return str(self)


class Scope:
    def __init__(self, parent=None):
        self.locals = []
        self.parent: Scope = parent
        self.children = []
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self):
        child = Scope(self)
        self.children.append(child)
        return child

    def define_variable(self, var_name, var_type, is_parameter=False) -> VariableInfo:
        info = VariableInfo(var_name, var_type, is_parameter)
        self.locals.append(info)
        return info

    def find_variable(self, var_name: str, index=None) -> VariableInfo:
        local_vars = self.locals if index is None else itt.islice(self.locals, index)
        try:
            return next(x for x in local_vars if x.name == var_name)
        except StopIteration:
            return self.parent.find_variable(var_name, self.index) if self.parent is not None else None

    def get_variables(self, all=False):
        vars = [x for x in self.locals]

        if all and self.parent is not None:
            vars.extend(self.parent.get_variables(True))

        return vars

    def is_defined(self, var_name: str) -> bool:
        return self.find_variable(var_name) is not None

    def is_local(self, var_name: str) -> bool:
        return any(True for x in self.locals if x.name == var_name)

    def inference_errors(self):
        errors = []
        for var in self.locals:
            errors.extend(var.inference_errors())
        for child_scope in self.children:
            errors.extend(child_scope.inference_errors())
        return errors

    def __str__(self):
        return self.tab_level(1, 1, 1)

    def tab_level(self, tabs, name, num) -> str:
        res = ('\t' * tabs) + ('\n' + ('\t' * tabs)).join(str(local) for local in self.locals)
        children = '\n'.join(child.tab_level(tabs + 1, num, num + 1) for child in self.children)
        return "\t" * (tabs - 1) + f'{name}' + "\t" * tabs + f'\n{res}\n{children}'

    def __repr__(self):
        return str(self)
