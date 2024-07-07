import Grammar.AST_nodes as nodes
import cmp.visitor as visitor
from Semantic.utils import Context


class CodeGenC(object):

    def __init__(self, context) -> None:
        self.index_var = 0
        self.context: Context = context

        self.blocks_defs = ""

        self.let_in_blocks = ""
        self.index_let_in_blocks = 0

        self.if_else_blocks = ""
        self.index_if_else_blocks = 0

        self.loop_blocks = ""
        self.index_loop_blocks = 0

        self.method_call_blocks = ""
        self.index_method_call_blocks = 0

        self.create_blocks = ""
        self.index_create_blocks = 0

        self.vector_comp = ""
        self.index_vector_comp = 0

        self.vector_selector = ""
        self.index_vector_selector = 0

        self.expression_block = ""
        self.index_expression_block = 0

    @staticmethod
    def get_lines_indented(code: str, add_return=False, collect_last_exp=False):
        lines = ["   " + line for line in code.split('\n') if len(line.strip(' ')) > 0]

        if add_return:
            lines[-1] = "   return " + lines[-1][3:] + ";"

        if collect_last_exp:
            lines[-1] = "   return_obj = " + lines[-1][3:] + ";"

        return '\n'.join(lines)
    
    
    @staticmethod
    def get_conditions(node: nodes.ConditionalNode):
        conditions=[]
        expressions=[]

        conditions.append(node.condition)
        expressions.append(node.expression)

        if(node.else_expr is None):
            return conditions,expressions
        else:
            c,e= CodeGenC.get_conditions(node.else_expr)
            conditions.extend(c)
            expressions.extend(e)
            return conditions,expressions
    
    @staticmethod
    def set_pi_and_e(str_: str):
        try:
            index_pi= str_.index("PI")
            str_=str_[:index_pi]+"createNumber(3.141592653589793)"+str_[index_pi+2:]
        except:
            pass
        try:
            index_e= str_.index("E")
            str_=str_[:index_e]+"createNumber(2.718281828459045)"+str_[index_e+1:]
        except:
            pass
        return str_



    @visitor.on('node')
    def visit(self, node):
        pass
        


    @visitor.when(nodes.TypeInstantiationNode)
    def visit(self, node: nodes.TypeInstantiationNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        create_block = "Object* createBlock" + str(self.index_create_blocks) + "("
        index = self.index_create_blocks
        self.index_create_blocks += 1

        for var in vars:
            create_block += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            create_block = create_block[:-2]

        create_block += ")"

        self.blocks_defs += create_block + ";\n\n"

        create_block += " {\n"

        def_vars = ""

        code = "   return create" + node.id + "("
        before = len(code)

        classs = self.context.get_type(node.id)
        args = node.args

        while classs is not None and classs.name != "Object":
            for i, param in enumerate(classs.params_names):
                var = "v" + str(self.index_var)
                self.index_var += 1

                def_vars += "   Object* " + var + " = " + self.visit(args[i]) + ";\n"
                classs.node.scope.children[0].find_variable(param).setNameC(var)

            for att in classs.attributes:
                code += "copyObject(" + self.visit(att.node.expr) + "), "

            args = classs.node.parent_args
            classs = classs.parent

        if before != len(code):
            code = code[:-2]

        code += ");"

        create_block += def_vars + "\n" + code + "\n}"
        self.create_blocks += create_block + "\n\n"

        params= self.set_pi_and_e(params)
        return "createBlock" + str(index) + params
    
    
    @visitor.when(nodes.MethodDeclarationNode)
    def visit(self, node: nodes.MethodDeclarationNode):
        return self.visit(node.expr)

    @visitor.when(nodes.FunctionDeclarationNode)
    def visit(self, node: nodes.FunctionDeclarationNode):
        return self.visit(node.expr)
    
    
    @visitor.when(nodes.ExpressionBlockNode)
    def visit(self, node: nodes.ExpressionBlockNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        code = "Object* expressionBlock" + str(self.index_expression_block) + "("
        index = self.index_expression_block
        self.index_expression_block += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        code += " {\n"

        expression_code = ""

        for expression in node.expressions:
            expression_code += self.visit(expression) + ";\n"

        expression_code = self.get_lines_indented(expression_code[:-2], True)

        code += expression_code

        code += "}"


        self.expression_block += code + "\n\n"
        params= self.set_pi_and_e(params)
        return "expressionBlock" + str(index) + params
    
    
    @visitor.when(nodes.PlusNode)
    def visit(self, node: nodes.PlusNode):
        return "numberSum(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(nodes.MinusNode)
    def visit(self, node: nodes.MinusNode):
        return "numberMinus(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(nodes.StarNode)
    def visit(self, node: nodes.StarNode):
        return "numberMultiply(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(nodes.DivNode)
    def visit(self, node: nodes.DivNode):
        return "numberDivision(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(nodes.PowNode)
    def visit(self, node: nodes.PowNode):
        return "numberPow(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(nodes.VariableNode)
    def visit(self, node: nodes.VariableNode):
        return node.scope.find_variable(node.lex).nameC
    
    
    @visitor.when(nodes.VarDeclarationNode)
    def visit(self, node: nodes.VarDeclarationNode):
        var = "v" + str(self.index_var)
        self.index_var += 1

        node.scope.find_variable(node.id).setNameC(var)

        return "Object* " + var + " = copyObject(" + self.visit(node.expr) + ");"

    @visitor.when(nodes.ConstantNumNode)
    def visit(self, node: nodes.ConstantNumNode):
        return "createNumber(" + node.lex + ")"

    @visitor.when(nodes.ConstantBoolNode)
    def visit(self, node: nodes.ConstantBoolNode):
        return "createBoolean(" + node.lex + ")"

    @visitor.when(nodes.ConstantStringNode)
    def visit(self, node: nodes.ConstantStringNode):
        #print(type(node.lex))
        return "createString(" + node.lex + ")"
    
    
    @visitor.when(nodes.LetInNode)
    def visit(self, node: nodes.LetInNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        code = "Object* letInNode" + str(self.index_let_in_blocks) + "("
        index = self.index_let_in_blocks
        self.index_let_in_blocks += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        code += " {\n"

        for var_declaration in node.var_declarations:
            code += "   " + self.visit(var_declaration) + "\n"

        code += self.get_lines_indented(self.visit(node.body), True) + "\n"
        code += "}"

        self.let_in_blocks += code + "\n\n"


        params= self.set_pi_and_e(params)
        return "letInNode" + str(index) + params
    
    
    @visitor.when(nodes.FunctionCallNode)
    def visit(self, node: nodes.FunctionCallNode):
        code = "function_" + node.id + "("

        for arg in node.args:
            code += "copyObject(" + self.visit(arg) + "), "

        if len(node.args) > 0:
            code = code[:-2]

        code += ")"

        return code
    
    
    @visitor.when(nodes.AsNode)
    def visit(self, node: nodes.AsNode):
        return self.visit(node.expression)
    
    @visitor.when(nodes.AttributeCallNode)
    def visit(self, node: nodes.AttributeCallNode):
        obj = self.visit(node.obj)

        type = node.scope.find_variable(obj).type

        if type.name == "Self":
            type = type.referred_type

        return "getAttributeValue(" + obj + ", \"" + type.name + "_" + node.attribute + "\")"
    
    
    @visitor.when(nodes.MethodCallNode)
    def visit(self, node: nodes.MethodCallNode):
        obj = self.visit(node.obj)

        args = ','.join(["Object*" for i in range(len(node.args))])

        if len(args) > 0:
            args = ',' + args

        if isinstance(node.obj, nodes.VariableNode):
            code = "((Object* (*)(Object*" + args + "))" + \
                   "getMethodForCurrentType(" + obj + ", \"" + node.method + "\", NULL)" + \
                   ")(" + obj

            for arg in node.args:
                code += ", copyObject(" + self.visit(arg) + ")"

            code += ")"

            return code

        else:
            vars = node.scope.get_variables(True)

            params = "("

            for var in vars:
                params += var.nameC + ", "

            if len(vars) > 0:
                params = params[:-2]

            params += ")"

            code = "Object* methodCallBlock" + str(self.index_method_call_blocks) + "("
            index = self.index_method_call_blocks
            self.index_method_call_blocks += 1

            for var in vars:
                code += "Object* " + var.nameC + ", "

            if len(vars) > 0:
                code = code[:-2]

            code += ")"

            self.blocks_defs += code + ";\n\n"

            code += " {\n"

            code += "   Object* obj = " + obj + ";\n"
            code += "   return ((Object* (*)(Object*" + args + "))" + \
                    "getMethodForCurrentType(obj, \"" + node.method + "\", NULL)" + \
                    ")(obj"

            for arg in node.args:
                code += ", copyObject(" + self.visit(arg) + ")"

            code += ");\n}"

            self.method_call_blocks += code + "\n\n"

            params= self.set_pi_and_e(params)
            return "methodCallBlock" + str(index) + params
        
        
    @visitor.when(nodes.ConditionalNode)
    def visit(self, node: nodes.ConditionalNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        code = "Object* ifElseBlock" + str(self.index_if_else_blocks) + "("
        index = self.index_if_else_blocks
        self.index_if_else_blocks += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        conditions,expressions= self.get_conditions(node)

        code += " {\n"

        code += "   if(*((bool*)getAttributeValue(" + self.visit(conditions[0]) + ", \"value\"))) {\n"

        code += self.get_lines_indented(self.get_lines_indented(self.visit(expressions[0]), True)) + "\n   }\n"

        for i in range(1, len(conditions)-1):
            code += "   else if(*((bool*)getAttributeValue(" + self.visit(conditions[i]) + ", \"value\"))) {\n"
            code += self.get_lines_indented(self.get_lines_indented(self.visit(expressions[i]), True)) + "\n   }\n"

        code += "   else {\n"
        code += self.get_lines_indented(self.get_lines_indented(self.visit(expressions[-1]), True)) + "\n   }\n"

        code += "}"

        self.if_else_blocks += code + "\n\n"

        params= self.set_pi_and_e(params)
        return "ifElseBlock" + str(index) + params
    
    
    @visitor.when(nodes.GreaterThanNode)
    def visit(self, node: nodes.GreaterThanNode):
        return "numberGreaterThan(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(nodes.GreaterOrEqualNode)
    def visit(self, node: nodes.GreaterOrEqualNode):
        return "numberGreaterOrEqualThan(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    
    
    @visitor.when(nodes.EqualNode)
    def visit(self, node: nodes.EqualNode):
        left = self.visit(node.left)

        if isinstance(node.left, nodes.VariableNode):
            code = "((Object* (*)(Object*, Object*))" + \
                   "getMethodForCurrentType(" + left + ", \"equals\", NULL)" + \
                   ")(" + left + ", " + self.visit(node.right) + ")"

            return code

        else:
            vars = node.scope.get_variables(True)

            params = "("

            for var in vars:
                params += var.nameC + ", "

            if len(vars) > 0:
                params = params[:-2]

            params += ")"

            code = "Object* methodCallBlock" + str(self.index_method_call_blocks) + "("
            index = self.index_method_call_blocks
            self.index_method_call_blocks += 1

            for var in vars:
                code += "Object* " + var.nameC + ", "

            if len(vars) > 0:
                code = code[:-2]

            code += ")"

            self.blocks_defs += code + ";\n\n"

            code += " {\n"

            code += "   Object* obj = " + left + ";\n"
            code += "   return ((Object* (*)(Object*, Object*))" + \
                    "getMethodForCurrentType(obj, \"equals\", NULL)" + \
                    ")(obj, " + self.visit(node.right) + ");"

            code += "\n}"

            self.method_call_blocks += code + "\n\n"

            params= self.set_pi_and_e(params)
            return "methodCallBlock" + str(index) + params
        
        
    @visitor.when(nodes.NotEqualNode)
    def visit(self, node: nodes.NotEqualNode):
        left = self.visit(node.left)

        if isinstance(node.left, nodes.VariableNode):
            code = "negBoolean(((Object* (*)(Object*, Object*))" + \
                   "getMethodForCurrentType(" + left + ", \"equals\", NULL)" + \
                   ")(" + left + ", " + self.visit(node.right) + "))"

            return code

        else:
            vars = node.scope.get_variables(True)

            params = "("

            for var in vars:
                params += var.nameC + ", "

            if len(vars) > 0:
                params = params[:-2]

            params += ")"

            code = "Object* methodCallBlock" + str(self.index_method_call_blocks) + "("
            index = self.index_method_call_blocks
            self.index_method_call_blocks += 1

            for var in vars:
                code += "Object* " + var.nameC + ", "

            if len(vars) > 0:
                code = code[:-2]

            code += ")"

            self.blocks_defs += code + ";\n\n"

            code += " {\n"

            code += "   Object* obj = " + left + ";\n"
            code += "   return negBoolean(((Object* (*)(Object*, Object*))" + \
                    "getMethodForCurrentType(obj, \"equals\", NULL)" + \
                    ")(obj, " + self.visit(node.right) + "));"

            code += "\n}"

            self.method_call_blocks += code + "\n\n"

            params= self.set_pi_and_e(params)
            return "methodCallBlock" + str(index) + params
        
        
    @visitor.when(nodes.LessThanNode)
    def visit(self, node: nodes.LessThanNode):
        return "numberLessThan(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(nodes.LessOrEqualNode)
    def visit(self, node: nodes.LessOrEqualNode):
        return "numberLessOrEqualThan(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    
    
    @visitor.when(nodes.WhileNode)
    def visit(self, node: nodes.WhileNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        code = "Object* loopBlock" + str(self.index_loop_blocks) + "("
        index = self.index_loop_blocks
        self.index_loop_blocks += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        code += " {\n"
        code += "   Object* return_obj = NULL;\n"

        code += "   while(*((bool*)getAttributeValue(" + self.visit(node.condition) + ", \"value\"))) {\n"
        code += self.get_lines_indented(self.get_lines_indented(self.visit(node.expression), False, True)) + "\n"
        code += "   }\n"

        code += "   return return_obj;\n}"

        self.loop_blocks += code + "\n\n"

        params= self.set_pi_and_e(params)
        return "loopBlock" + str(index) + params
    
    
    @visitor.when(nodes.DestructiveAssignmentNode)
    def visit(self, node: nodes.DestructiveAssignmentNode):
        return "replaceObject(" + self.visit(node.id) + ", " + self.visit(node.expr) + ")"

    @visitor.when(nodes.ModNode)
    def visit(self, node: nodes.ModNode):
        return "numberMod(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"


    @visitor.when(nodes.VectorInitializationNode)
    def visit(self, node: nodes.VectorInitializationNode):
        return "createVector(" + str(len(node.elements)) + ", " + ", ".join(
            [self.visit(element) for element in node.elements]) + ")"
    
    
    @visitor.when(nodes.VectorComprehensionNode)
    def visit(self, node: nodes.VectorComprehensionNode):
        var_iter = "v" + str(self.index_var)
        self.index_var += 1
        node.scope.children[0].find_variable(node.var).setNameC(var_iter)

        selector = "Object* selector" + str(self.index_vector_selector) + " ("
        index_selector = self.index_vector_selector
        self.index_vector_selector += 1

        vars = node.scope.get_variables(True)

        for var in vars:
            selector += "Object* " + var.nameC + ", "

        selector += "Object* " + var_iter

        selector += ")"

        self.blocks_defs += selector + ";\n\n"

        selector += " {\n"
        selector += self.get_lines_indented(self.visit(node.function), True) + "\n}"

        self.vector_selector += selector + "\n\n"

        vector_comp = "Object* vectorComprehension" + str(self.index_vector_comp) + " ("
        index_vec = self.index_vector_comp
        self.index_vector_comp += 1

        for var in vars:
            vector_comp += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            vector_comp = vector_comp[:-2]

        vector_comp += ")"

        self.blocks_defs += vector_comp + ";\n\n"

        vector_comp += " {\n"

        vector_comp += "   Object* iterable = " + self.visit(node.iterable) + ";\n"
        vector_comp += "   Object*(*next)(Object*) = getMethodForCurrentType(iterable, \"next\", NULL);\n"
        vector_comp += "   Object*(*current)(Object*) = getMethodForCurrentType(iterable, \"current\", NULL);\n\n"
        vector_comp += "   int size = *(int*)getAttributeValue(iterable, \"size\");\n\n"

        vector_comp += "   Object** new_list = malloc(size * sizeof(Object*));\n\n"

        vector_comp += "   for(int i = 0; i < size; i++) {\n"
        vector_comp += "      next(iterable);\n"
        vector_comp += "      new_list[i] = selector" + str(index_selector)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        vector_comp += params + "current(iterable));\n"

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        vector_comp += "   }\n\n"
        vector_comp += "   return createVectorFromList(size, new_list);\n"
        vector_comp += "}"

        self.vector_comp += vector_comp + "\n\n"

        params= self.set_pi_and_e(params)
        return "vectorComprehension" + str(index_vec) + params
    
    
    @visitor.when(nodes.IndexingNode)
    def visit(self, node: nodes.IndexingNode):
        return "getElementOfVector(" + self.visit(node.obj) + ", " + self.visit(node.index) + ")"
    
    
    @visitor.when(nodes.ForNode)
    def visit(self, node: nodes.ForNode):
        var_iter = "v" + str(self.index_var)
        self.index_var += 1
        node.scope.children[0].find_variable(node.var).setNameC(var_iter)

        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        code = "Object* loopBlock" + str(self.index_loop_blocks) + "("
        index = self.index_loop_blocks
        self.index_loop_blocks += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        code += " {\n"
        code += "   Object* return_obj = NULL;\n"
        code += "   Object* " + var_iter + " = NULL;\n"
        code += "   Object* iterable = " + self.visit(node.iterable) + ";\n"
        code += "   Object*(*next)(Object*) = getMethodForCurrentType(iterable, \"next\", NULL);\n"
        code += "   Object*(*current)(Object*) = getMethodForCurrentType(iterable, \"current\", NULL);\n\n"

        code += "   while(*(bool*)getAttributeValue(next(iterable), \"value\")) {\n"
        code += "      " + var_iter + " = current(iterable);\n\n"
        code += self.get_lines_indented(self.get_lines_indented(self.visit(node.expression), False, True)) + "\n"
        code += "   }\n"

        code += "   return return_obj;\n}"

        self.loop_blocks += code + "\n\n"

        params= self.set_pi_and_e(params)
        return "loopBlock" + str(index) + params
    
    
    @visitor.when(nodes.OrNode)
    def visit(self, node: nodes.OrNode):
        return "boolOr(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(nodes.AndNode)
    def visit(self, node: nodes.AndNode):
        return "boolAnd(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    
    
    @visitor.when(nodes.ConcatNode)
    def visit(self, node: nodes.ConcatNode):
        return "stringConcat(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    

    @visitor.when(nodes.DoubleConcatNode)
    def visit(self, node: nodes.DoubleConcatNode):
        return "stringDoubleConcat(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    
    
    @visitor.when(nodes.BaseCallNode)
    def visit(self, node: nodes.BaseCallNode):
        code = "((Object* (*)(Object*"

        for i in range(len(node.args)):
            code += ", Object*"

        code += "))getMethodForCurrentType(self, \"" + node.method_name + "\", \"" + node.parent_type.name + "\"))(self"

        for arg in node.args:
            code += ", " + self.visit(arg)

        code += ")"

        return code
    
    
    @visitor.when(nodes.IsNode)
    def visit(self, node: nodes.IsNode):
        try:
            self.context.get_type(node.type)
            return "isType(" + self.visit(node.expression) + ", \"" + node.type + "\")"
        except:
            return "isProtocol(" + self.visit(node.expression) + ", \"" + node.type + "\")"