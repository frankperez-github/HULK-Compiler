from code_visitor import CodeGenC



class CCodeGenerator:
    def __call__(self, ast, context):
        with open('c_base.c') as c_tools:
            return c_tools.read() + "\n\n" + self.generate(ast, context)
        
        
    @staticmethod
    def generate(ast, context):

        def get_lines_indented(code: str, add_return=False):
            lines = ["   " + line for line in code.split('\n') if len(line.strip(' ')) > 0]

            if add_return:
                lines[-1] = "   return " + lines[-1][3:] + ";"

            return '\n'.join(lines)

        type_conforms_to_protocols = {}

        for ttype in context.types.values():
            type_conforms_to_protocols[ttype.name] = []

            for protocol in context.protocols.values():
                if ttype.conforms_to(protocol):
                    type_conforms_to_protocols[ttype.name].append(protocol)

        codgen = CodeGenC(context)

        declarations = ""
        type_create = ""
        methods_code = ""
        functions_code = ""
        main = ""

        create_defs = {}
        method_defs = {}
        function_defs = []

        for type in context.types.values():
            if type.name not in ["Number", "Boolean", "String", "Object", "Range"]:
                create_def = "Object* create" + type.name + " ("
                create_params = []

                current = type

                while current is not None:
                    for att in current.attributes:
                        create_params.append(current.name + "_" + att.name)
                        create_def += "Object* " + create_params[-1] + ", "

                    current = current.parent

                if len(create_params) > 0:
                    create_def = create_def[:-2]

                create_def += ")"

                create_defs[type.name] = (create_def, create_params)

                declarations += create_def + ";\n"

                method_defs[type.name] = []

                for method in type.methods:
                    method_name = "method_" + type.name + "_" + method.name
                    method_def = "Object* " + method_name + " (Object* self"

                    method.node.scope.children[0].find_variable("self").setNameC("self")

                    for i, name in enumerate(method.param_names):
                        id_param = "p" + str(i)
                        method.node.scope.children[0].find_variable(name).setNameC(id_param)
                        method_def += ", Object* " + id_param

                    method_def += ")"
                    method_defs[type.name].append((method_def, method_name, method))
                    declarations += method_def + ";\n"

                declarations += "\n"

                
        for function in context.functions.values():
            if function.name not in ['print', 'sqrt', 'sin', 'cos', 'exp', 'log', 'rand', 'range', 'parse']:
                function_name = "function_" + function.name
                function_def = "Object* " + function_name + " ("

                for i, name in enumerate(function.param_names):
                    id_param = "p" + str(i)
                    function.node.scope.children[0].find_variable(name).setNameC(id_param)
                    function_def += "Object* " + id_param + ", "

                if len(function.param_names):
                    function_def = function_def[:-2]

                function_def += ")"
                function_defs.append((function_def, function_name, function))
                declarations += function_def + ";\n"

        declarations += '\n'

        
        for type in context.types.values():
            if type.name not in ["Number", "Boolean", "String", "Object", "Range"]:
                type_create += create_defs[type.name][0] + " {\n"
                type_create += "   Object* obj = createObject();\n"

                type_create += "\n"
                for param in create_defs[type.name][1]:
                    type_create += "   setAttribute(obj, \"" + param + "\", " + param + ");\n"

                type_create += "\n"

                current = type
                index = 0
                while current is not None:
                    type_create += "   setAttribute(obj, \"parent_type" + str(
                        index) + "\", \"" + current.name + "\");\n"

                    if current.name in method_defs:
                        for method in method_defs[current.name]:
                            type_create += "   setAttribute(obj, \"" + method[1] + "\", *" + method[1] + ");\n"

                    current = current.parent
                    index += 1

                type_create += "\n"
                index = 0
                for protocol in type_conforms_to_protocols[type.name]:
                    type_create += "   setAttribute(obj, \"conforms_protocol" + str(
                        index) + "\", \"" + protocol.name + "\");\n"
                    index += 1

                type_create += "   return obj;\n"
                type_create += "}\n\n"

                
        for type in context.types.values():
            if type.name not in ["Number", "Boolean", "String", "Object", "Range"]:
                if type.name in method_defs:
                    for method_def, method_name, method in method_defs[type.name]:
                        methods_code += method_def + " {\n"
                        methods_code += "   if(self == NULL)\n"
                        methods_code += "       throwError(\"Null Reference\");\n\n"
                        methods_code += get_lines_indented(codgen.visit(method.node), True) + "\n"
                        methods_code += "}\n\n"

        for function_def, function_name, function in function_defs:
            functions_code += function_def + " {\n"
            functions_code += get_lines_indented(codgen.visit(function.node), True) + "\n"
            functions_code += "}\n\n"

            
        main += "\nint main() {\n"
        main += "   srand(time(NULL));\n\n"

        main += get_lines_indented(codgen.visit(ast.expression)) + ";"

        main += "\n   return 0; \n}"

        return declarations + type_create + codgen.blocks_defs + codgen.expression_block + codgen.let_in_blocks + codgen.if_else_blocks + codgen.loop_blocks + codgen.method_call_blocks + codgen.create_blocks + codgen.vector_selector + codgen.vector_comp + methods_code + functions_code + main