from cmp.pycompiler import Grammar
import AST_nodes as nodes

G = Grammar()

#NonTerminals 

program = G.NonTerminal('<program>', startSymbol= True)

expr, expr_bloq, expr_simp, expr_lis, end_expr = G.NonTerminals('<expr> <expr_bloq> <expr_simp> <expr_lis> <end_expr>')

declarations, asign_destruct = G.NonTerminals('<declarations> <asign_destruct>')

or_expr, and_expr, not_expr = G.NonTerminals('<or_expr> <and_expr> <not_expr>')

eq_or_deq_expr, ineq_expr = G.NonTerminals('<eq_or_deq_expr> <ineq_expr>')

is_or_as_expr, concat_expr = G.NonTerminals('<is_or_as_expr> <concat_expr>')

sum_or_minus_expr, star_div_mod_expr, sign_expr, pow_expr = (
    G.NonTerminals('<sum_or_minus_expr> <star_div_mod_expr> <sign_expr> <pow_expr>'))

type_inst = G.NonTerminal('<type_inst>') 

index_meth_attr = G.NonTerminal('<index_meth_attr>')

factor, atom = G.NonTerminals('<factor> <atom>')

dec_meth, type_decl, dec_func,  = G.NonTerminals('<dec_meth> <type_decl> <dec_func>')

opt_type, opt_param_lis, opt_her, optional_param = (
    G.NonTerminals('opt_type <opt_param_lis> <opt_her> <optional_param>'))

param_lis, param, attr = G.NonTerminals('<param_lis> <param> <attr>')

let_in, if_expr, else_expr  = G.NonTerminals('<let_in> <if_expr> <else_expr>')

while_expr, for_expr = G.NonTerminals('<while_expr> <for_expr>')

asignaciones, asign, asign_simpl = G.NonTerminals('<asignaciones> <asign> <asign_simpl>')

feature_lis, feature_lis_or_eps= G.NonTerminals('<feature_lis> <feature_lis_or_eps>')

func_call, func_lis, sing_func = G.NonTerminals('<func_call> <func_lis> <sing_func>')

opt_arg_lis, arg_lis = G.NonTerminals('<opt_arg_lis> <arg_lis>')

dec_protocol, opt_ext = G.NonTerminals('<dec_protocol> <opt_ext>')

ob_params_ann_lis_or_eps, ob_params_ann_lis, ob_params_ann = (
    G.NonTerminals('<ob_params_ann_lis_or_eps> <ob_params_ann_lis> <ob_params_ann>'))

vector_innit = G.NonTerminal('<vector_innit>')

type_ann = G.NonTerminal('<type_ann>')


# Terminals 

obra, cbra, opar, cpar, ocor, ccor, d_bar = G.Terminals('{ } ( ) [ ] ||')

dot, semi, colon, semicolon, arrow = G.Terminals('. , : ; =>')

or_, and_, not_ = G.Terminals('| & !')

d_as, s_as, new_  = G.Terminals(':= = new')

eq, neq, leq, geq, lt, gt = G.Terminals('== != <= >= < >')

is_, as_ = G.Terminals('is as')

arr, d_arr = G.Terminals('@ @@')

plus, minus, star, div, mod, pow_, pow__ = G.Terminals('+ - * / % ^ **')

bool_, str_, number_, id_ = G.Terminals('<bool> <string> <number> <id>')

let_, in_ = G.Terminals('let in')

if_, else_, elif_ = G.Terminals('if else elif')

while_, for_ = G.Terminals('while for')

inherits, function, protocol, extends, type_, base_ = G.Terminals('inherits function protocol extends type base')


#productions

program %= expr_simp, lambda h,s: nodes.ProgramNode([],s[1])
program %= end_expr, lambda h,s: nodes.ProgramNode([],s[1])
program %= declarations + expr_simp, lambda h,s: nodes.ProgramNode(s[1],s[2])
program %= declarations + end_expr, lambda h,s: nodes.ProgramNode(s[1],s[2])

declarations %= declarations + dec_func, lambda h,s: s[1]+[s[2]]
declarations %= dec_func, lambda h,s: [s[1]]
declarations %= declarations + type_decl, lambda h,s: s[1]+[s[2]]
declarations %= type_decl, lambda h,s: [s[1]]
declarations %= declarations + protocol, lambda h,s: s[1]+[s[2]]
declarations %= protocol, lambda h,s: [s[1]]

expr %= expr_bloq, lambda h,s: s[1]
expr %= expr_simp, lambda h,s: s[1]

expr_bloq %= obra + expr_lis + cbra, lambda h,s: nodes.ExpressionBlockNode(s[2])

expr_lis %= end_expr + expr_lis, lambda h,s: [s[1]]+ s[2]
expr_lis %= end_expr, lambda h,s: [s[1]]
expr_lis %= expr_simp, lambda h,s: [s[1]]

expr_simp %= if_expr, lambda h,s: s[1]
expr_simp %= let_in, lambda h,s: s[1]
expr_simp %= while_expr, lambda h,s: s[1]
expr_simp %= for_expr, lambda h,s: s[1]
expr_simp %= asign_destruct, lambda h,s: s[1]

end_expr %= expr + semicolon, lambda h,s: s[1]
end_expr %= expr_bloq, lambda h,s: s[1]

asign_destruct %= or_expr + d_as + asign_destruct, (
    lambda h,s: nodes.DestructiveAssignmentNode(s[1],s[3]))
asign_destruct %= or_expr, lambda h,s: s[1]

or_expr %= or_expr + or_ + and_expr, lambda h,s: nodes.OrNode(s[1],s[3])
or_expr %= and_expr, lambda h,s: s[1]

and_expr %= and_expr + and_ + eq_or_deq_expr, lambda h,s: nodes.AndNode(s[1],s[3])
and_expr %= eq_or_deq_expr, lambda h,s: s[1]

eq_or_deq_expr %= eq_or_deq_expr + eq + ineq_expr, lambda h,s: nodes.EqualNode(s[1],s[3])
eq_or_deq_expr %= eq_or_deq_expr + neq + ineq_expr, lambda h,s: nodes.NotEqualNode(s[1],s[3])
eq_or_deq_expr %= ineq_expr, lambda h,s: s[1]

ineq_expr %= ineq_expr + leq + is_or_as_expr, lambda h,s: nodes.LessOrEqualNode(s[1],s[3])
ineq_expr %= ineq_expr + geq + is_or_as_expr, lambda h,s: nodes.GreaterOrEqualNode(s[1],s[3])
ineq_expr %= ineq_expr + gt + is_or_as_expr, lambda h,s: nodes.GreaterThanNode(s[1],s[3])
ineq_expr %= ineq_expr + lt + is_or_as_expr, lambda h,s: nodes.LessThanNode(s[1],s[3])
ineq_expr %= is_or_as_expr, lambda h,s: s[1]

is_or_as_expr %= concat_expr + is_ + id_, lambda h,s: nodes.IsNode(s[1],s[3])
is_or_as_expr %= concat_expr + as_ + id_, lambda h,s: nodes.AsNode(s[1],s[3])
is_or_as_expr %= concat_expr, lambda h,s: s[1]

concat_expr %= concat_expr + arr + sum_or_minus_expr, lambda h,s: nodes.ConcatNode(s[1],s[3])
concat_expr %= concat_expr + d_arr + sum_or_minus_expr, lambda h,s: nodes.DoubleConcatNode(s[1],s[3])
concat_expr %= sum_or_minus_expr, lambda h,s: s[1]

sum_or_minus_expr %= sum_or_minus_expr + plus + star_div_mod_expr, lambda h,s: nodes.PlusNode(s[1],s[3])
sum_or_minus_expr %= sum_or_minus_expr + minus + star_div_mod_expr, lambda h,s:nodes.MinusNode(s[1],s[3])
sum_or_minus_expr %= star_div_mod_expr, lambda h,s: s[1]

star_div_mod_expr %= star_div_mod_expr + star + sign_expr, lambda h,s: nodes.StarNode(s[1],s[3])
star_div_mod_expr %= star_div_mod_expr + div + sign_expr, lambda h,s: nodes.DivNode(s[1],s[3])
star_div_mod_expr %= star_div_mod_expr + mod + sign_expr, lambda h,s: nodes.ModNode(s[1],s[3])
star_div_mod_expr %= sign_expr, lambda h,s: s[1]

sign_expr %= plus + pow_expr, lambda h,s: s[2]
sign_expr %= minus + pow_expr, lambda h,s: nodes.NegNode(s[2])
sign_expr %= pow_expr, lambda h,s: s[1]

pow_expr %= type_inst + pow_ + pow_expr, lambda h,s: nodes.PowNode(s[1],s[3],s[2])
pow_expr %= type_inst + pow__ + pow_expr, lambda h,s: nodes.PowNode(s[1],s[3],s[2])
pow_expr %= type_inst, lambda h,s: s[1]

type_inst %= new_ + id_ + opar + opt_arg_lis + cpar, lambda h,s: nodes.TypeInstantiationNode(s[2],s[4])
type_inst %= not_expr, lambda h,s: s[1]

not_expr %= not_ + index_meth_attr, lambda h,s: nodes.NotNode(s[2])
not_expr %= index_meth_attr, lambda h,s: s[1]

index_meth_attr %= index_meth_attr + dot + id_ + opar + opt_arg_lis + cpar, (
                            lambda h,s: nodes.MethodCallNode(s[1],s[3],s[5])
                            )
index_meth_attr %= index_meth_attr + dot + id_, lambda h,s: nodes.AttributeCallNode(s[1],s[3])
index_meth_attr %= index_meth_attr + ocor + expr + ccor, lambda h,s: nodes.IndexingNode(s[1],s[3])
index_meth_attr %= factor, lambda h,s: s[1]

factor %= opar + expr + cpar , lambda h,s: s[2]
factor %= atom, lambda h,s: s[1]

atom %= number_ , lambda h,s: nodes.ConstantNumNode(s[1])
atom %= str_, lambda h,s: nodes.ConstantStringNode(s[1])
atom %= bool_, lambda h,s: nodes.ConstantBoolNode(s[1])
atom %= id_ , lambda h,s: nodes.VariableNode(s[1])
atom %= func_call, lambda h,s: s[1]
atom %= vector_innit, lambda h,s: s[1]
atom %= base_ + opar + opt_arg_lis + cpar, lambda h,s: nodes.BaseCallNode(s[3])


dec_meth %= id_ + opar + opt_param_lis + cpar + opt_type + arrow + expr_simp + semicolon, (
                                                lambda h,s: nodes.MethodDeclarationNode(s[1],s[3],s[7],s[5])
                                               )
dec_meth %= id_ + opar + opt_param_lis + cpar + opt_type + expr_bloq , lambda h,s: nodes.MethodDeclarationNode(s[1],s[3],s[6],s[5])
dec_meth %= id_ + opar + opt_param_lis + cpar + opt_type + expr_bloq + semicolon , lambda h,s: nodes.MethodDeclarationNode(s[1],s[3],s[6],s[5])

opt_type %= G.Epsilon, lambda h,s: None
opt_type %= colon + type_ann, lambda h,s: s[2]

type_ann %= id_, lambda h,s: s[1]
type_ann %= type_ann + ocor + ccor, lambda h,s: nodes.VectorTypeAnnotationNode(s[1]) 

opt_param_lis %= param_lis, lambda h,s: s[1]
opt_param_lis %= G.Epsilon, lambda h,s: []

param_lis %= param, lambda h,s: [s[1]]
param_lis %= param_lis + semi + param, lambda h,s: s[1] + [s[3]]

param %= id_ + opt_type, lambda h,s: (s[1],s[2])

let_in %= let_ + asignaciones + in_ + expr, lambda h,s: nodes.LetInNode(s[2],s[4])

asignaciones %= asignaciones + semi + asign, lambda h,s: s[1] + [s[3]] 
asignaciones %= asign , lambda h,s: [s[1]]

#asign %= asign_simpl, lambda h,s: s[1]
#asign %= asign_destruct, lambda h,s: s[1]
asign %= id_ + opt_type + s_as + expr, lambda h,s: nodes.VarDeclarationNode(s[1],s[4],s[2])

#end_expr
#asign_simpl %= param + s_as + expr, lambda h,s: nodes.VarDeclarationNode(s[1][0],s[3],s[1][1])

#############
if_expr %= if_ + opar + expr + cpar + expr + else_expr, lambda h,s: nodes.ConditionalNode(s[3],s[5],s[6])

else_expr %= elif_ + opar + expr + cpar + expr + else_expr, lambda h,s: nodes.ConditionalNode(s[3],s[5],s[6])
else_expr %= else_ + expr, lambda h,s: nodes.ConditionalNode(None,s[2],None)
############


while_expr %= while_ + opar + expr + cpar + expr, lambda h,s: nodes.WhileNode(s[3],s[5])

for_expr %= for_ + opar + id_ + in_ + expr + cpar + expr, lambda h,s: nodes.ForNode(s[3],s[5],s[7])

type_decl %= type_ + id_ + optional_param + opt_her + obra + feature_lis_or_eps + cbra, lambda h,s: nodes.TypeDeclarationNode(s[2],s[3],s[6],s[4][0],s[4][1])
#type_decl %= type_ + id_ + optional_param + opt_her +obra + feature_lis_or_eps + cbra, lambda h,s: nodes.TypeDeclarationNode(s[2],s[3],s[5],None,None)
#type_decl %= type_ + id_ + optional_param + inherits + id_ + opar + opt_arg_lis + cpar + obra + feature_lis_or_eps + cbra, lambda h,s:  nodes.TypeDeclarationNode(s[2],s[3],s[8],s[5],s[6]) 


opt_her %= inherits + id_ , lambda h,s: (s[2],[])
opt_her %= inherits + id_ + opar +opt_arg_lis + cpar , lambda h,s: (s[2],s[4])
opt_her %= G.Epsilon, lambda h,s: (None,None)

optional_param %= opar + param_lis + cpar, lambda h,s: s[2]
optional_param %= G.Epsilon, lambda h,s: []

#dec_func %= function + dec_meth, lambda h,s: s[2]
dec_func %= function + id_ + opar + opt_param_lis + cpar + opt_type + arrow + expr_simp + semicolon, (lambda h,s: nodes.FunctionDeclarationNode(s[2],s[4],s[8],s[6]))
dec_func %= function + id_ + opar + opt_param_lis + cpar + opt_type + expr_bloq , lambda h,s: nodes.FunctionDeclarationNode(s[2],s[4],s[7],s[6])
dec_func %= function + id_ + opar + opt_param_lis + cpar + opt_type + expr_bloq + semicolon , lambda h,s: nodes.FunctionDeclarationNode(s[2],s[4],s[7],s[6])


feature_lis_or_eps %= G.Epsilon, lambda h,s: []
feature_lis_or_eps%= feature_lis, lambda h,s: s[1]

feature_lis %= feature_lis + attr, lambda h,s: s[1] + [s[2]]
feature_lis %= feature_lis + dec_meth , lambda h,s: s[1] + [s[2]]
feature_lis %= attr, lambda h,s: [s[1]]
feature_lis %= dec_meth, lambda h,s: [s[1]]

#attr %= param + s_as + end_expr, lambda h,s: nodes.AttributeDeclarationNode(s[1][0],s[3],s[1][1])
attr %= id_ + opt_type + s_as + end_expr, lambda h,s: nodes.AttributeDeclarationNode(s[1],s[4],s[2])


func_call %= id_ + opar + opt_arg_lis + cpar, lambda h,s: nodes.FunctionCallNode(s[1],s[3])

opt_arg_lis %= G.Epsilon, lambda h,s: []
opt_arg_lis %= arg_lis, lambda h,s: s[1]

arg_lis %= expr, lambda h,s: [s[1]]
arg_lis %= expr + semi + arg_lis, lambda h,s: [s[1]] + s[3]

dec_protocol %= protocol + id_ + opt_ext + obra + func_lis + cbra, lambda h,s: nodes.ProtocolDeclarationNode(s[2],s[5],s[3])

opt_ext %= G.Epsilon, lambda h,s: None
opt_ext %= extends + id_, lambda h,s: s[2]

func_lis %= func_lis + sing_func, lambda h,s: s[1] + [s[2]]
func_lis %= sing_func, lambda h,s: [s[1]]

sing_func %= id_ + opar + ob_params_ann_lis_or_eps + cpar + colon + type_ann +semicolon, lambda h,s: nodes.MethodSignatureDeclarationNode(s[1],s[3],s[6])

ob_params_ann_lis_or_eps %= ob_params_ann_lis, lambda h,s: s[1]
ob_params_ann_lis_or_eps %= G.Epsilon, lambda h,s: None

ob_params_ann_lis %= ob_params_ann, lambda h,s: [s[1]]
ob_params_ann_lis %= ob_params_ann + semi + ob_params_ann_lis, lambda h,s: [s[1]] + s[3]

ob_params_ann %= id_ + colon + type_ann, lambda h,s: (s[1],s[3])

vector_innit %= ocor + opt_arg_lis + ccor, lambda h,s: nodes.VectorInitializationNode(s[2])
vector_innit %= ocor + expr + d_bar + id_ + in_ + expr + ccor, lambda h,s: nodes.VectorComprehensionNode(s[2],s[4],s[6])




