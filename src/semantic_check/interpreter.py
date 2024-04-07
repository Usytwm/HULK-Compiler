from copy import deepcopy
import math
import random
import re
from src.tools.ast_nodes import *
from src.cmp.semantic import *
import src.cmp.visitor as visitor


class InterpreterScope(Scope):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.var_values = dict()

    def create_child(self):
        child = InterpreterScope(self)
        self.children.append(child)
        return child

    def define_variable(self, vname, vtype, value):
        info = VariableInfo(vname, vtype)
        self.local_variables.add(info)
        self.var_values[vname] = value
        return info

    def find_variable_value(self, vname, index=None):
        locals = (
            self.local_variables
            if index is None
            else itt.islice(self.local_variables, index)
        )
        try:
            return next((x, self.var_values[x.name]) for x in locals if x.name == vname)
        except StopIteration:
            return (
                self.parent.find_variable_value(vname, self.index)
                if not self.parent is None
                else None
            ), None

    def set_variable_value(self, vname, value, index=0):
        for x in self.local_variables:
            if x.name == vname:
                self.var_values[x.name] = value
                return

        return (
            self.parent.find_variable_value(vname, self.index)
            if not self.parent is None
            else None
        )


class InterpreterMethod(Method):
    def __init__(self, name, param_names, params_types, return_type, body):
        super().__init__(name, param_names, params_types, return_type)
        self.body = body


class InterpreterAttribute(Attribute):
    def __init__(self, name, typex, value):
        super().__init__(name, typex)
        self.value = value


class TreeInterpreter:

    def __init__(self, context):
        self.context: Context = context
        self.scope = InterpreterScope()
        self.errors = []
        self.currentType: Type = None

    @visitor.on("node")
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for statement in node.statments:
            self.visit(statement, self.scope)

    @visitor.when(PrintStatmentNode)
    def visit(self, node: PrintStatmentNode, scope: InterpreterScope):
        _, value = self.visit(node.expression, scope)
        print(value)
        return self.context.get_type("string"), value

    # TODO Pendiente
    @visitor.when(IdentifierNode)
    def visit(self, node: IdentifierNode, scope: InterpreterScope):
        try:
            var, value = scope.find_variable_value(node.id)
            return var.type, value
        except:
            return self.context.get_type("any"), None

    @visitor.when(NumberNode)
    def visit(self, node: NumberNode, scope: InterpreterScope):
        return self.context.get_type("number"), float(node.value)

    @visitor.when(StringNode)
    def visit(self, node: StringNode, scope: InterpreterScope):
        word = node.value[1 : len(node.value) - 1]
        return self.context.get_type("string"), str(word)

    @visitor.when(BooleanNode)
    def visit(self, node: BooleanNode, scope: InterpreterScope):
        try:
            return self.context.get_type("bool"), eval(node.value)
        except:
            return self.context.get_type("any"), None

    @visitor.when(KernAssigmentNode)
    def visit(self, node: KernAssigmentNode, scope: InterpreterScope):
        type, value = self.visit(node.expression, scope)
        scope.define_variable(node.id.id, type, value)

        return type, value

    @visitor.when(DestroyNode)
    def visit(self, node: DestroyNode, scope: InterpreterScope):
        type, value = self.visit(node.expression, scope)
        scope.set_variable_value(node.id.id, value)

        return type, value

    @visitor.when(TypeNode)
    def visit(self, node: TypeNode, scope: InterpreterScope):
        try:
            type = self.context.types[node.type]
            return type, type
        except:
            return self.context.get_type("any"), None

    @visitor.when(TypeDefinitionNode)
    def visit(self, node: TypeDefinitionNode, scope: InterpreterScope):
        pass

    @visitor.when(FunctionDefinitionNode)
    def visit(self, node: FunctionDefinitionNode, scope: InterpreterScope):
        if self.currentType:
            try:
                self.scope.node[self.currentType.name].append(node)
            except:
                self.scope.node[self.currentType.name] = [node]
        else:
            try:
                self.scope.node[None].append(node)
            except:
                self.scope.node[None] = [node]

    @visitor.when(FunctionCallNode)
    def visit(self, node: FunctionCallNode, scope: InterpreterScope):
        function = list(
            filter(
                lambda x: len(x.parameters) == len(node.args), self.scope.node[node.id]
            )
        )[0]

        for statment in function.body:
            self.visit(statment)

    @visitor.when(IfStructureNode)
    def visit(self, node: IfStructureNode, scope: InterpreterScope):
        _, condition = self.visit(node.condition, scope)
        if condition:
            return self.visit_body(node.body, scope)
        elif len(node._elif) != 0:
            for elif_node in node._elif:
                _, elif_condition = self.visit(elif_node.condition, scope)
                if elif_condition:
                    return self.visit_body(elif_node.body, scope)

        return self.visit_body(node._else.body, scope)

    def visit_body(self, node, scope):
        result = self.context.get_type("any"), None
        if type(node) == list:
            for statement in node:
                result = self.visit(statement, scope)
            return result
        return self.visit(node, scope)

    @visitor.when(WhileStructureNode)
    def visit(self, node: WhileStructureNode, scope: InterpreterScope):
        result = self.context.get_type("any"), None
        inner_scope = scope.create_child()
        _, condition_value = self.visit(node.condition, scope)
        while condition_value:
            result = self.visit_body(node.body, inner_scope)
            _, condition_value = self.visit(node.condition, scope)
        return result

    @visitor.when(ForStructureNode)
    def visit(self, node: ForStructureNode, scope: InterpreterScope):
        result = self.context.get_type("any"), None
        inner_scope = scope.create_child()
        self.visit(node.init_assigments, inner_scope)
        _, condition_value = self.visit(node.condition, inner_scope)
        while condition_value:
            result = self.visit_body(node.body, inner_scope)
            self.visit(node.increment_condition, inner_scope)
            _, condition_value = self.visit(node.condition, inner_scope)

        return result

    @visitor.when(CollectionNode)
    def visit(self, node: CollectionNode, scope):
        result = self.context.get_type("any"), None
        if len(node.collection) != 0:
            for statement in node.collection:
                result = self.visit(statement, scope)

        return result

    @visitor.when(BoolIsTypeNode)
    def visit(self, node: BoolIsTypeNode, scope: InterpreterScope):
        lef_type, _ = self.visit(node.left, scope)
        right_type, _ = self.visit(node.right, scope)
        return self.context.get_type("bool"), lef_type.conforms_to(right_type.name)

    @visitor.when(BoolAndNode)
    def visit(self, node: BoolAndNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("bool"), left_value and right_value

    @visitor.when(BoolOrNode)
    def visit(self, node: BoolOrNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("bool"), left_value or right_value

    @visitor.when(BoolNotNode)
    def visit(self, node: BoolNotNode, scope: InterpreterScope):
        _, value = self.visit(node.node, scope)
        return self.context.get_type("bool"), not value

    @visitor.when(BoolCompLessNode)
    def visit(self, node: BoolCompLessNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("bool"), left_value < right_value

    @visitor.when(BoolCompGreaterNode)
    def visit(self, node: BoolCompGreaterNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("bool"), left_value > right_value

    @visitor.when(BoolCompLessEqualNode)
    def visit(self, node: BoolCompLessEqualNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("bool"), left_value <= right_value

    @visitor.when(BoolCompGreaterEqualNode)
    def visit(self, node: BoolCompGreaterEqualNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("bool"), left_value >= right_value

    @visitor.when(BoolCompEqualNode)
    def visit(self, node: BoolCompEqualNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("bool"), left_value == right_value

    @visitor.when(BoolCompNotEqualNode)
    def visit(self, node: BoolCompNotEqualNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("bool"), left_value != right_value

    @visitor.when(PlusExpressionNode)
    def visit(self, node: PlusExpressionNode, scope: InterpreterScope):
        _, left_value = self.visit(node.expression_1, scope)
        _, right_value = self.visit(node.expression_2, scope)
        return self.context.get_type("number"), left_value + right_value

    @visitor.when(SubsExpressionNode)
    def visit(self, node: SubsExpressionNode, scope: InterpreterScope):
        _, left_value = self.visit(node.expression_1, scope)
        _, right_value = self.visit(node.expression_2, scope)
        return self.context.get_type("number"), left_value - right_value

    @visitor.when(DivExpressionNode)
    def visit(self, node: DivExpressionNode, scope: InterpreterScope):
        _, left_value = self.visit(node.expression_1, scope)
        _, right_value = self.visit(node.expression_2, scope)
        if right_value == 0:
            raise Exception(f"Se esta realizando una division entre 0. {node.location}")
        return self.context.get_type("number"), left_value / right_value

    @visitor.when(MultExpressionNode)
    def visit(self, node: MultExpressionNode, scope: InterpreterScope):
        _, left_value = self.visit(node.expression_1, scope)
        _, right_value = self.visit(node.expression_2, scope)
        return self.context.get_type("number"), left_value * right_value

    @visitor.when(ModExpressionNode)
    def visit(self, node: ModExpressionNode, scope: InterpreterScope):
        _, left_value = self.visit(node.expression_1, scope)
        _, right_value = self.visit(node.expression_2, scope)
        if right_value == 0:
            raise Exception(f"Se esta realizando una division entre 0. {node.location}")
        return self.context.get_type("number"), left_value % right_value

    @visitor.when(PowExpressionNode)
    def visit(self, node: PowExpressionNode, scope: InterpreterScope):
        _, left_value = self.visit(node.expression_1, scope)
        _, right_value = self.visit(node.expression_2, scope)
        return self.context.get_type("number"), left_value**right_value

    @visitor.when(SqrtMathNode)
    def visit(self, node: SqrtMathNode, scope: InterpreterScope):
        _, expression_value = self.visit(node.node, scope)
        if expression_value < 0:
            raise Exception(
                f"Esta tratando de calcular la raiz cuadrada de unnumero negativo. {node.location}"
            )
        return self.context.get_type("number"), math.sqrt(expression_value)

    @visitor.when(SinMathNode)
    def visit(self, node: SinMathNode):
        _, expression_value = self.visit(node.node)
        return self.context.get_type("number"), math.sin(expression_value)

    @visitor.when(CosMathNode)
    def visit(self, node: CosMathNode, scope: InterpreterScope):
        _, expression_value = self.visit(node.node, scope)
        return self.context.get_type("number"), math.cos(expression_value)

    @visitor.when(TanMathNode)
    def visit(self, node: TanMathNode, scope: InterpreterScope):
        _, expression_value = self.visit(node.node, scope)
        # Convert the expression value to radians if it's in degrees
        if isinstance(expression_value, (int, float)):
            expression_value = math.radians(expression_value)
        # Check if the value is within the range where tan is undefined
        if math.isclose(expression_value, math.pi / 2, rel_tol=1e-9) or math.isclose(
            expression_value, 3 * math.pi / 2, rel_tol=1e-9
        ):
            raise Exception(
                f"La tangente no esta definida para 90 grados o multiplos de 180 grados. {node.location}"
            )
        return self.context.get_type("number"), math.tan(expression_value)

    @visitor.when(ExpMathNode)
    def visit(self, node: ExpMathNode, scope: InterpreterScope):
        _, expression_value = self.visit(node.node, scope)
        return self.context.get_type("number"), math.exp(expression_value)

    @visitor.when(RandomFunctionCallNode)
    def visit(self, node: RandomFunctionCallNode, scope: InterpreterScope):
        return self.context.get_type("number"), random.random()

    @visitor.when(LogFunctionCallNode)
    def visit(self, node: LogFunctionCallNode, scope: InterpreterScope):
        _, base_value = self.visit(node.base)
        _, expression_value = self.visit(node.expression, scope)
        if expression_value <= 0:
            raise Exception(
                f"El logaritmo no esta definido para numeros menores o iguales a 0. {node.location}"
            )
        return self.context.get_type("number"), math.log(expression_value, base_value)

    @visitor.when(StringConcatNode)
    def visit(self, node: StringConcatNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("string"), str(left_value) + str(right_value)

    @visitor.when(StringConcatWithSpaceNode)
    def visit(self, node: StringConcatWithSpaceNode, scope: InterpreterScope):
        _, left_value = self.visit(node.left, scope)
        _, right_value = self.visit(node.right, scope)
        return self.context.get_type("string"), str(left_value) + " " + str(right_value)


# class ScopeInterprete(Scope):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.variable = {}

#     def asign_variable(self, name, value):
#         self.variable[name] = value
#         self.define_variable(name, value)

#     def get_variable(self, name):
#         return self.variable.get(name, None)

#     def create_child(self):
#         child = ScopeInterprete(self)
#         child.node = self.node
#         child.variable = deepcopy(self.variable)
#         self.children.append(child)
#         return child


# class ContextInterprete(Context):
#     def __init__(self):
#         super().__init__()
#         self.node = {}

#     def create_node(self, name, node):
#         self.node[name] = [node]

#     def get_node(self, name):
#         return self.node.get(name, None)


# class TreeWalkInterpreter:

#     def __init__(self):
#         self.context = ContextInterprete()
#         self.scope = ScopeInterprete()
#         self.errors = []
#         self.currentType: Type = None

#     @visitor.on("node")
#     def visit(self, node, tabs):
#         pass

#     @visitor.when(ProgramNode)
#     def visit(self, node: ProgramNode):
#         for statement in node.statments:
#             self.visit(statement, self.scope, self.context)

#     @visitor.when(CollectionNode)
#     def visit(self, node: CollectionNode, scope: Scope = None, Context: Context = None):
#         ret = None
#         for element in node.collection:
#             ret = self.visit(element, scope, Context)
#         return ret

#     @visitor.when(LetInExpressionNode)
#     def visit(
#         self, node: LetInExpressionNode, scope: Scope = None, Context: Context = None
#     ):

#         self.visit(node.assigments, scope, Context)
#         ret = None
#         if isinstance(node.body, List):
#             for statment in node.body:
#                 ret = self.visit(statment, scope, Context)
#             return ret
#         else:
#             return self.visit(node.body, scope, Context)

#     @visitor.when(KernAssigmentNode)
#     def visit(
#         self, node: KernAssigmentNode, scope: Scope = None, Context: Context = None
#     ):
#         scope.asign_variable(node.id.id, self.visit(node.expression, scope))
#         return scope.get_variable(node.id.id)

#     @visitor.when(KernInstanceCreationNode)
#     def visit(
#         self,
#         node: KernInstanceCreationNode,
#         scope: Scope = None,
#         Context: Context = None,
#     ):
#         return node

#     @visitor.when(DestroyNode)
#     def visit(self, node: DestroyNode, scope: Scope = None, Context: Context = None):
#         scope.asign_variable(node.id.id, self.visit(node.expression, scope))
#         return scope.get_variable(node.id.id)

#     @visitor.when(PrintStatmentNode)
#     def visit(
#         self, node: PrintStatmentNode, scope: Scope = None, Context: Context = None
#     ):
#         value = self.visit(node.expression, scope, Context)
#         print(value)
#         return value

#     # @visitor.when(MemberAccessNode)
#     # !a,i tengo que arreglarlo ;ara que devuelva lo correcto, eso implica arreglar cosas en la definicion de un tipo y en la asignacion
#     # def visit(
#     #     self, node: MemberAccessNode, scope: Scope = None, Context: Context = None
#     # ):

#     #     type = self.context.get_node(node.type.id)

#     #     for i, param in enumerate(function.parameters):
#     #         scope.asign_variable(
#     #             list(param.keys())[0].id, self.visit(node.args[i], scope, Context)
#     #         )
#     #     ret = None
#     #     for statment in function.body:
#     #         ret = self.visit(statment, scope, Context)
#     #     return ret

#     @visitor.when(NumberNode)
#     def visit(self, node: NumberNode, scope: Scope = None, Context: Context = None):
#         return float(node.value)

#     @visitor.when(StringNode)
#     def visit(self, node: StringNode, scope: Scope = None, Context: Context = None):
#         value = re.sub(r'^"|"$', "", node.value)
#         return value

#     @visitor.when(TypeDefinitionNode)
#     def visit(
#         self, node: TypeDefinitionNode, scope: Scope = None, context: Context = None
#     ):

#         self.currentType = self.context.create_type(node.id)
#         child = scope.create_child()
#         for method in node.methods:
#             self.visit(method, child, context)

#         self.context.create_node(node.id, node)
#         if node.inheritance:
#             try:
#                 node.methods.extends(self.context.get_node(node.inheritance).methods)
#             except:
#                 node.methods.extend([])
#         self.currentType = None

#     @visitor.when(FunctionDefinitionNode)
#     def visit(
#         self, node: FunctionDefinitionNode, scope: Scope = None, Context: Context = None
#     ):
#         if self.currentType:
#             try:
#                 self.scope.node[self.currentType.name].append(node)
#             except:
#                 self.scope.node[self.currentType.name] = [node]
#         else:
#             try:
#                 self.scope.node[None].append(node)
#             except:
#                 self.scope.node[None] = [node]
#         for param in node.parameters:
#             arg, type_att = list(param.keys())[0].id, list(param.values())[0]
#             scope.define_variable(arg, type_att)

#     @visitor.when(FunctionCallNode)
#     def visit(
#         self, node: FunctionCallNode, scope: Scope = None, Context: Context = None
#     ):
#         if self.currentType:
#             function = list(
#                 filter(
#                     lambda x: len(x.parameters) == len(node.args),
#                     scope.node[self.currentType.name],
#                 )
#             )[0]
#         else:
#             function = list(
#                 filter(
#                     lambda x: len(x.parameters) == len(node.args),
#                     scope.node[None],
#                 )
#             )[0]

#         for i, param in enumerate(function.parameters):
#             scope.asign_variable(
#                 list(param.keys())[0].id, self.visit(node.args[i], scope, Context)
#             )
#         ret = None
#         for statment in function.body:
#             ret = self.visit(statment, scope, Context)
#         return ret

#     @visitor.when(IfStructureNode)
#     def visit(
#         self, node: IfStructureNode, scope: Scope = None, Context: Context = None
#     ):
#         condition = self.visit(node.condition, scope, Context)
#         ret = None
#         if condition:
#             inner_scope = scope.create_child()
#             for statments in node.body:
#                 ret = self.visit(statments, inner_scope, Context)
#         elif node._elif:
#             for elif_node in node._elif:
#                 elif_condition = self.visit(elif_node.condition, scope, Context)
#                 inner_scope = scope.create_child()
#                 if elif_condition:
#                     for statments in elif_node.body:
#                         ret = self.visit(statments, inner_scope, Context)

#                     break
#             else:
#                 if node._else:
#                     inner_scope = scope.create_child()
#                     for statments in node._else.body:
#                         ret = self.visit(statments, inner_scope, Context)
#         else:
#             if node._else:
#                 inner_scope = scope.create_child()
#                 for statments in node._else.body:
#                     ret = self.visit(statments, inner_scope, Context)

#         return ret

#     @visitor.when(WhileStructureNode)
#     def visit(
#         self, node: WhileStructureNode, scope: Scope = None, Context: Context = None
#     ):
#         ret = None
#         while self.visit(node.condition, scope, Context):
#             for statment in node.body:
#                 ret = self.visit(statment, scope, Context)
#         return ret

#     @visitor.when(IdentifierNode)
#     def visit(self, node: IdentifierNode, scope: Scope = None, Context: Context = None):
#         return scope.get_variable(node.id)

#     @visitor.when(ForStructureNode)
#     def visit(
#         self, node: ForStructureNode, scope: Scope = None, Context: Context = None
#     ):
#         self.visit(node.init_assigments, scope, Context)
#         ret = None
#         while self.visit(node.condition, scope, Context):
#             for statment in node.body:
#                 ret = self.visit(statment, scope, Context)
#                 self.visit(node.increment_condition, scope, Context)
#         return ret

#     @visitor.when(BoolIsTypeNode)
#     def visit(self, node: BoolIsTypeNode, scope: Scope = None, Context: Context = None):
#         value = self.visit(node.left, scope, Context)
#         return isinstance(value, node.right)

#     @visitor.when(BoolAndNode)
#     def visit(self, node: BoolAndNode, scope: Scope = None, Context: Context = None):
#         left_value = self.visit(node.left, scope, Context)
#         right_value = self.visit(node.right, scope, Context)
#         return left_value and right_value

#     @visitor.when(BoolOrNode)
#     def visit(self, node: BoolOrNode, scope: Scope = None, Context: Context = None):
#         left_value = self.visit(node.left, scope, Context)
#         right_value = self.visit(node.right, scope, Context)
#         return left_value or right_value

#     @visitor.when(BoolNotNode)
#     def visit(self, node: BoolNotNode, scope: Scope = None, Context: Context = None):
#         value = self.visit(node.node, scope, Context)
#         return not value

#     @visitor.when(BoolCompLessNode)
#     def visit(
#         self, node: BoolCompLessNode, scope: Scope = None, Context: Context = None
#     ):
#         left_value = self.visit(node.left, scope, Context)
#         right_value = self.visit(node.right, scope, Context)
#         return left_value < right_value

#     @visitor.when(BoolCompGreaterNode)
#     def visit(
#         self, node: BoolCompGreaterNode, scope: Scope = None, Context: Context = None
#     ):
#         left_value = self.visit(node.left, scope, Context)
#         right_value = self.visit(node.right, scope, Context)
#         return left_value > right_value

#     @visitor.when(BooleanNode)
#     def visit(self, node: BooleanNode, scope: Scope = None, Context: Context = None):
#         return node.value

#     @visitor.when(BoolCompLessEqualNode)
#     def visit(
#         self, node: BoolCompLessEqualNode, scope: Scope = None, Context: Context = None
#     ):
#         left_value = self.visit(node.left, scope, Context)
#         right_value = self.visit(node.right, scope, Context)
#         return left_value <= right_value

#     @visitor.when(BoolCompGreaterEqualNode)
#     def visit(
#         self,
#         node: BoolCompGreaterEqualNode,
#         scope: Scope = None,
#         Context: Context = None,
#     ):
#         left_value = self.visit(node.left, scope, Context)
#         right_value = self.visit(node.right, scope, Context)
#         return left_value >= right_value

#     @visitor.when(BoolCompEqualNode)
#     def visit(
#         self, node: BoolCompEqualNode, scope: Scope = None, Context: Context = None
#     ):
#         left_value = self.visit(node.left, scope, Context)
#         right_value = self.visit(node.right, scope, Context)
#         return left_value == right_value

#     @visitor.when(BoolCompNotEqualNode)
#     def visit(
#         self, node: BoolCompNotEqualNode, scope: Scope = None, Context: Context = None
#     ):
#         left_value = self.visit(node.left)
#         right_value = self.visit(node.right)
#         return left_value != right_value

#     @visitor.when(PlusExpressionNode)
#     def visit(
#         self, node: PlusExpressionNode, scope: Scope = None, Context: Context = None
#     ):
#         iner_scope_left = scope.create_child()
#         left_value = self.visit(node.expression_1, iner_scope_left, Context)
#         iner_scope_right = scope.create_child()
#         right_value = self.visit(node.expression_2, iner_scope_right, Context)
#         return left_value + right_value

#     @visitor.when(SubsExpressionNode)
#     def visit(
#         self, node: SubsExpressionNode, scope: Scope = None, Context: Context = None
#     ):
#         iner_scope_left = scope.create_child()
#         left_value = self.visit(node.expression_1, iner_scope_left, Context)
#         iner_scope_right = scope.create_child()
#         right_value = self.visit(node.expression_2, iner_scope_right, Context)
#         return left_value - right_value

#     @visitor.when(DivExpressionNode)
#     def visit(
#         self, node: DivExpressionNode, scope: Scope = None, Context: Context = None
#     ):
#         iner_scope_left = scope.create_child()
#         left_value = self.visit(node.expression_1, iner_scope_left, Context)
#         iner_scope_right = scope.create_child()
#         right_value = self.visit(node.expression_2, iner_scope_right, Context)
#         return left_value / right_value

#     @visitor.when(MultExpressionNode)
#     def visit(
#         self, node: MultExpressionNode, scope: Scope = None, Context: Context = None
#     ):
#         iner_scope_left = scope.create_child()
#         left_value = self.visit(node.expression_1, iner_scope_left, Context)
#         iner_scope_right = scope.create_child()
#         right_value = self.visit(node.expression_2, iner_scope_right, Context)
#         return left_value * right_value

#     @visitor.when(ModExpressionNode)
#     def visit(
#         self, node: ModExpressionNode, scope: Scope = None, Context: Context = None
#     ):
#         iner_scope_left = scope.create_child()
#         left_value = self.visit(node.expression_1, iner_scope_left, Context)
#         iner_scope_right = scope.create_child()
#         right_value = self.visit(node.expression_2, iner_scope_right, Context)
#         return left_value % right_value

#     @visitor.when(PowExpressionNode)
#     def visit(
#         self, node: PowExpressionNode, scope: Scope = None, Context: Context = None
#     ):
#         iner_scope_left = scope.create_child()
#         left_value = self.visit(node.expression_1, iner_scope_left, Context)
#         iner_scope_right = scope.create_child()
#         right_value = self.visit(node.expression_2, iner_scope_right, Context)
#         return left_value**right_value

#     @visitor.when(SqrtMathNode)
#     def visit(self, node: SqrtMathNode, scope: Scope = None, Context: Context = None):
#         iner_scope = scope.create_child()
#         expression_value = self.visit(node.node, iner_scope, Context)
#         return math.sqrt(expression_value)

#     @visitor.when(SinMathNode)
#     def visit(self, node: SinMathNode, scope: Scope = None, Context: Context = None):
#         expression_value = self.visit(node.node, scope, Context)
#         try:
#             return math.sin(expression_value)
#         except:
#             raise Exception(
#                 f"La función requerida sin no está definida en {expression_value}."
#             )

#     @visitor.when(CosMathNode)
#     def visit(self, node: CosMathNode, scope: Scope = None, Context: Context = None):
#         expression_value = self.visit(node.node, scope, Context)
#         try:
#             return math.cos(expression_value)
#         except:
#             raise Exception(
#                 f"La función requerida cos no está definida en {expression_value}."
#             )

#     @visitor.when(TanMathNode)
#     def visit(self, node: TanMathNode, scope: Scope = None, Context: Context = None):
#         expression_value = self.visit(node.node, scope, Context)
#         try:
#             return math.tan(expression_value)
#         except:
#             raise Exception(
#                 f"La función requerida tan no está definida en {expression_value}."
#             )

#     @visitor.when(ExpMathNode)
#     def visit(self, node: ExpMathNode, scope: Scope = None, Context: Context = None):
#         expression_value = self.visit(node.node, scope, Context)
#         return math.exp(expression_value)

#     @visitor.when(RandomFunctionCallNode)
#     def visit(
#         self, node: RandomFunctionCallNode, scope: Scope = None, Context: Context = None
#     ):
#         return random.random()

#     @visitor.when(LogFunctionCallNode)
#     def visit(
#         self, node: LogFunctionCallNode, scope: Scope = None, Context: Context = None
#     ):
#         base_value = self.visit(node.base, scope, Context)
#         expression_value = self.visit(node.expression, scope, Context)
#         try:
#             return math.log(expression_value, base_value)
#         except ValueError:
#             # Lanzar un error personalizado indicando que el logaritmo no está definido para los valores dados
#             raise Exception(
#                 "El logaritmo no está definido para los valores proporcionados."
#             )
#         except Exception as e:
#             # Captura cualquier otro tipo de excepción y lanza un error personalizado
#             raise Exception(
#                 f"Ocurrió un error inesperado al intentar calcular el logaritmo: {e}."
#             )

#     @visitor.when(StringConcatNode)
#     def visit(
#         self, node: StringConcatNode, scope: Scope = None, Context: Context = None
#     ):
#         left_value = self.visit(node.left, scope, Context)
#         right_value = self.visit(node.right, scope, Context)
#         return str(left_value) + str(right_value)

#     @visitor.when(StringConcatWithSpaceNode)
#     def visit(
#         self,
#         node: StringConcatWithSpaceNode,
#         scope: Scope = None,
#         Context: Context = None,
#     ):
#         left_value = self.visit(node.left, scope, Context)
#         right_value = self.visit(node.right, scope, Context)
#         return str(left_value) + " " + str(right_value)
