from errors import HulkSemanticError

class Attribute:
    def __init__(self, name, typex, node=None):
        self.name = name
        self.type = typex
        self.node = node

    
    def inference_errors(self):
        errors = []
        if self.type == AutoType() and not self.type.is_error():
            errors.append(HulkSemanticError(HulkSemanticError.CANNOT_INFER_ATTR_TYPE % (self.name, self.node.line, self.node.column)))
            self.type = ErrorType()
        return errors
    
    def __str__(self):
        return f'[attrib] {self.name} : {self.type.name};'

    def __repr__(self):
        return str(self)


class Method:
    def __init__(self, name, param_names, params_types, return_type, node=None):
        self.name = name
        self.node = node
        self.param_names = param_names
        self.param_types = params_types
        self.param_vars = []
        self.return_type = return_type


    def can_substitute_with(self, other):
        if self.name != other.name:
            return False
        if not other.return_type.conforms_to(self.return_type):
            return False
        if len(self.param_types) != len(other.param_types):
            return False
        for meth_type, impl_type in zip(self.param_types, other.param_types):
            if not meth_type.conforms_to(impl_type):
                return False
        return True
    
    
    def inference_errors(self):
        errors = []

        for i, param_type in enumerate(self.param_types):
            if isinstance(param_type, AutoType) and not param_type.is_error():
                param_name = self.param_names[i]
                error_message = HulkSemanticError.CANNOT_INFER_PARAM_TYPE % (param_name, self.name,self.node.line, self.node.column)
                errors.append(HulkSemanticError(error_message))
                self.param_types[i] = ErrorType()

        if self.return_type == AutoType() and not self.return_type.is_error():
            errors.append(HulkSemanticError(HulkSemanticError.CANNOT_INFER_RETURN_TYPE % self.name, self.node.line, self.node.column))
            self.return_type = ErrorType()
        return errors
    
    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n, t in zip(self.param_names, self.param_types))
        return f'[method] {self.name}({params}): {self.return_type.name};'

    def __eq__(self, other):
        return other.name == self.name and \
            other.return_type == self.return_type and \
            other.param_types == self.param_types
    

class Protocol:
    def __init__(self, name: str, node=None):
        self.name = name
        self.node = node
        self.methods = []
        self.parent = None

    def set_parent(self, parent):
        if self.parent is not None:
            raise HulkSemanticError(f'Parent type is already set for {self.name}. Near line: {self.node.line}, column: {self.node.column}')
        self.parent = parent

    def get_method(self, name: str):
        try:
            return next(method for method in self.methods if method.name == name)
        except StopIteration:
            if self.parent is None:
                raise HulkSemanticError(f'Method "{name}" is not defined in {self.name}. Near line: {self.node.line}, column: {self.node.column}')
            try:
                return self.parent.get_method(name)
            except HulkSemanticError:
                raise HulkSemanticError(f'Method "{name}" is not defined in {self.name}. Near line: {self.node.line}, column: {self.node.column}')

    def define_method(self, name: str, param_names: list, param_types: list, return_type, node=None):
        if name in (method.name for method in self.methods):
            raise HulkSemanticError(f'Method "{name}" already defined in {self.name}. Near line: {self.node.line}, column: {self.node.column}')
        method = Method(name, param_names, param_types, return_type, node)
        self.methods.append(method)
        return method

    def get_all_methods(self):
        if(self.parent is None):
            return self.methods
        else: return self.methods + self.parent.get_all_methods()
    
    def _not_ancestor_conforms_to(self, other):
        if not isinstance(other, Protocol):
            return False
        try:
            return all(method.can_substitute_with(self.get_method(method.name)) for method in other.get_all_methods())
        # If a method is not defined in the current type (or its ancestors), then it is not conforming
        except HulkSemanticError:
            return False

    def conforms_to(self, other):
        if other == ObjectType():
            return True
        elif isinstance(other, Type):
            return False
        return self == other or (self.parent is not None and self.parent.conforms_to(
            other)) or self._not_ancestor_conforms_to(other)

    @staticmethod
    def is_error():
        return False

    def __str__(self):
        output = f'protocol {self.name}'
        parent = '' if self.parent is None else f' extends {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.methods else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)




class Type:
    def __init__(self, name: str, node=None):
        self.name = name
        self.node = node
        self.params_names = []
        self.params_types = []
        self.param_vars = []
        self.attributes= []
        self.methods= []
        self.parent = None
        self.looked_for_parent_params = False

    def set_parent(self, parent):
        if self.parent is not None:
            raise HulkSemanticError(f'Parent type is already set for {self.name}. Near line: {self.node.line}, column: {self.node.column}')
        self.parent = parent

    def get_attribute(self, name: str) -> Attribute:
        try:
            return next(attr for attr in self.attributes if attr.name == name)
        except StopIteration:
            if self.node is not None:
                raise HulkSemanticError(f'Attribute "{name}" is not defined in {self.name}. Near line: {self.node.line}, column: {self.node.column}')
            else:
                raise HulkSemanticError(f'Attribute "{name}" is not defined in {self.name}.')

    def define_attribute(self, name: str, typex, node=None) -> Attribute:
        try:
            self.get_attribute(name)
        except HulkSemanticError:
            attribute = Attribute(name, typex, node)
            self.attributes.append(attribute)
            return attribute
        else:
            raise HulkSemanticError(f'Attribute "{name}" is already defined in {self.name}. Near line: {self.node.line}, column: {self.node.column}')

    def get_method(self, name: str) -> Method:
        try:
            return next(method for method in self.methods if method.name == name)
        except StopIteration:
            if self.parent is None:
                if self.node is not None:
                    raise HulkSemanticError(f'Method "{name}" is not defined in {self.name}. Near line: {self.node.line}, column: {self.node.column}')
                else: raise HulkSemanticError(f'Method "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_method(name)
            except HulkSemanticError:
                if self.node is not None:
                    raise HulkSemanticError(f'Method "{name}" is not defined in {self.name}. Near line: {self.node.line}, column: {self.node.column}')
                else: raise HulkSemanticError(f'Method "{name}" is not defined in {self.name}.')

    def define_method(self, name: str, param_names: list, param_types: list, return_type, node=None) -> Method:
        if name in (method.name for method in self.methods):
            raise HulkSemanticError(f'Method "{name}" already defined in {self.name}. Near line: {self.node.line}, column: {self.node.column}')
        method = Method(name, param_names, param_types, return_type, node)
        self.methods.append(method)
        return method
    
    
    def set_params(self):
        """
        Sets the params of the type.
        If the type doesn't specify them, sets a copy of the params of the lowest ancestor that does it.
        """
        params_names, params_types = self.get_params()
        self.params_names = params_names
        self.params_types = params_types

    def get_params(self):
        if (self.params_names == [] or self.params_types == []) and self.parent is not None:
            params_names, params_types = self.parent.get_params()
        else:
            params_names = self.params_names
            params_types = self.params_types
        return params_names, params_types
    
    def conforms_to(self, other):
        if isinstance(other, Type):
            return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)
        elif isinstance(other, Protocol):
            try:
                return all(method.can_substitute_with(self.get_method(method.name)) for method in other.get_all_methods())
            # If a method is not defined in the current type (or its ancestors), then it is not conforming
            except HulkSemanticError:
                return False


    def inference_errors(self):
        if self.is_error():
            return []
        errors = []
        for attr in self.attributes:
            errors.extend(attr.inference_errors())
        for method in self.methods:
            errors.extend(method.inference_errors())
        for i, param_type in enumerate(self.params_types):
            if isinstance(param_type, AutoType):
                param_name = self.params_names[i]
                error_message = HulkSemanticError.CANNOT_INFER_PARAM_TYPE % (param_name, self.name, self.node.line, self.node.column)
                errors.append(HulkSemanticError(error_message))
                self.params_types[i] = ErrorType()
        return errors
    
    def is_error(self):
        return False

    def bypass(self):
        return False

    def __str__(self):
        output = f'type {self.name}'
        params = '' if not self.params_names else ','.join(
            [f"{param_name} {param_type.name}" for param_name, param_type in zip(self.params_names, self.params_types)])
        output += params
        parent = '' if self.parent is None else f' inherits {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(x) for x in self.attributes)
        output += '\n\t' if self.attributes else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)



class ErrorType(Type):
    def __init__(self):
        Type.__init__(self, '<error>')

    def conforms_to(self, other):
        return True

    def bypass(self):
        return True

    def is_error(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Type)


class AutoType(Type):
    def __init__(self):
        Type.__init__(self, '<auto>')

    def __eq__(self, other):
        return isinstance(other, AutoType) or other.name == self.name


class StringType(Type):
    def __init__(self):
        super().__init__('String')
        self.set_parent(ObjectType())

    def __eq__(self, other):
        return isinstance(other, StringType) or other.name == self.name


class BoolType(Type):
    def __init__(self):
        super().__init__('Boolean')
        self.set_parent(ObjectType())

    def __eq__(self, other):
        return isinstance(other, BoolType) or other.name == self.name


class NumberType(Type):
    def __init__(self) -> None:
        super().__init__('Number')
        self.set_parent(ObjectType())

    def __eq__(self, other):
        return isinstance(other, NumberType) or other.name == self.name


class ObjectType(Type):
    def __init__(self) -> None:
        super().__init__('Object')

    def __eq__(self, other):
        return isinstance(other, ObjectType) or other.name == self.name


class SelfType(Type):
    def __init__(self, referred_type: Type = None) -> None:
        super().__init__('Self')
        self.referred_type = referred_type

    def get_attribute(self, name: str) -> Attribute:
        if self.referred_type:
            return self.referred_type.get_attribute(name)

        return super().get_attribute(name)

    def __eq__(self, other):
        return isinstance(other, SelfType) or other.name == self.name


class VectorType(Type):
    def __init__(self, element_type) -> None:
        super().__init__(f'{element_type.name}[]')
        self.set_parent(ObjectType())
        self.define_method('size', [], [], NumberType())
        self.define_method('next', [], [], BoolType())
        self.define_method('current', [], [], element_type)


    
    def conforms_to(self, other):
        if not isinstance(other, VectorType):
            return super().conforms_to(other)
        self_elem_type = self.get_element_type()
        other_elem_type = other.get_element_type()
        return self_elem_type.conforms_to(other_elem_type)
    
    def get_element_type(self):
        return self.get_method('current').return_type

    def __eq__(self, other):
        return isinstance(other, VectorType) or other.name == self.name
    


def _get_lca(type1: Type, type2: Type):
    # Object is the "root" of protocols too
    if type1 is None or type2 is None:
        return ObjectType()
    if type1.conforms_to(type2):
        return type2
    if type2.conforms_to(type1):
        return type1
    return _get_lca(type1.parent, type2.parent)


def get_lowest_common_ancestor(types):
    """
    Get the lowest common ancestor of a list of types.
    If there is some ErrorType in the list, it will return an ErrorType.
    If there is some AutoType in the list, it will return an AutoType.
    If there is no lca, it will return Object, ie: lca of Hashable and Iterable is Object.

    :param types: List of types
    :type types: List[Union[Type, Protocol]]
    :return: The lowest common ancestor of the types.
    :rtype: Type or Protocol
    """
    if not types or any(isinstance(t, ErrorType) for t in types):
        return ErrorType()
    if any(t == AutoType() for t in types):
        return AutoType()
    lca = types[0]
    for typex in types[1:]:
        lca = _get_lca(lca, typex)
    return lca


def get_most_specialized_type(types, var_name: str):
    """
    Get the most specialized type in a list of types.
    If there is some ErrorType in the list, it will return an ErrorType.
    If there is some AutoType in the list, it will return an AutoType.
    If there is no specialized type, it will raise a HulkSemanticError.

    :param types: List of types or protocols
    :type types: List[Union[Type, Protocol]]
    :param var_name: Name of the variable that is being checked.
    :return: The most specialized type in the list.
    :rtype: Type or Protocol
    """
    if not types or any(isinstance(t, ErrorType) for t in types):
        return ErrorType()
    if any(isinstance(t, AutoType) for t in types):
        return AutoType()
    most_specialized = types[0]
    for typex in types[1:]:
        if typex.conforms_to(most_specialized):
            most_specialized = typex
        elif not most_specialized.conforms_to(typex):
            raise HulkSemanticError(HulkSemanticError.INCONSISTENT_USE % (var_name,'0', '0'))
    return most_specialized