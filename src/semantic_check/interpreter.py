import math
import random
from src.tools.ast_nodes import *
from src.cmp.semantic import *
import src.cmp.visitor as visitor


class ScopeInterprete(Scope):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.variable = {}

    def asign_variable(self, name, value):
        self.variable[name] = value
        self.define_variable(name, value)

    def get_variable(self, name):
        return self.variable.get(name, None)


class TreeWalkInterpreter:

    def __init__(self):
        self.context = Context()
        self.scope = ScopeInterprete()
        self.errors = []
        self.currentType: Type = None

    @visitor.on("node")
    def visit(self, node, tabs):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for statement in node.statments:
            self.visit(statement, self.scope, self.context)

    @visitor.when(CollectionNode)
    def visit(self, node: CollectionNode, scope: Scope = None, Context: Context = None):
        for element in node.collection:
            self.visit(element, scope, Context)

    @visitor.when(LetInExpressionNode)
    def visit(
        self, node: LetInExpressionNode, scope: Scope = None, Context: Context = None
    ):

        self.visit(node.assigments, scope, Context)
        ret = None
        for statment in node.body:
            ret = self.visit(statment, scope, Context)
        return ret

    @visitor.when(KernAssigmentNode)
    def visit(
        self, node: KernAssigmentNode, scope: Scope = None, Context: Context = None
    ):
        scope.asign_variable(node.id.id, self.visit(node.expression, scope))
        return scope.get_variable(node.id.id)

    @visitor.when(DestroyNode)
    def visit(self, node: DestroyNode, scope: Scope = None, Context: Context = None):
        scope.asign_variable(node.id.id, self.visit(node.expression, scope))
        return scope.get_variable(node.id.id)

    @visitor.when(PrintStatmentNode)
    def visit(
        self, node: PrintStatmentNode, scope: Scope = None, Context: Context = None
    ):
        value = self.visit(node.expression, scope, Context)
        print(value)
        return value

    @visitor.when(NumberNode)
    def visit(self, node: NumberNode, scope: Scope = None, Context: Context = None):
        return float(node.value)

    @visitor.when(StringNode)
    def visit(self, node: StringNode, scope: Scope = None, Context: Context = None):
        return node.value

    @visitor.when(TypeDefinitionNode)
    def visit(
        self, node: TypeDefinitionNode, scope: Scope = None, context: Context = None
    ):
        context = Context()
        self.currentType = context.create_type(node.id)
        child = scope.create_child()
        for method in node.methods:
            self.visit(method, child, context)
        self.currentType = None

    @visitor.when(FunctionDefinitionNode)
    def visit(
        self, node: FunctionDefinitionNode, scope: Scope = None, Context: Context = None
    ):
        if self.currentType:
            try:
                scope.node[self.currentType.name].append(node)
            except:
                scope.node[self.currentType.name] = [node]
        else:
            try:
                scope.node[None].append(node)
            except:
                scope.node[None] = [node]
        for param in node.parameters:
            arg, type_att = list(param.keys())[0].id, list(param.values())[0]
            scope.define_variable(arg, type_att)

    @visitor.when(FunctionCallNode)
    def visit(
        self, node: FunctionCallNode, scope: Scope = None, Context: Context = None
    ):
        if self.currentType:
            function = list(
                filter(
                    lambda x: len(x.parameters) == len(node.args),
                    scope.node[self.currentType.name],
                )
            )[0]
        else:
            function = list(
                filter(
                    lambda x: len(x.parameters) == len(node.args),
                    scope.node[None],
                )
            )[0]

        for i, param in enumerate(function.parameters):
            scope.asign_variable(
                list(param.keys())[0].id, self.visit(node.args[i], scope, Context)
            )
        ret = None
        for statment in function.body:
            ret = self.visit(statment, scope, Context)
        return ret

    @visitor.when(IfStructureNode)
    def visit(
        self, node: IfStructureNode, scope: Scope = None, Context: Context = None
    ):
        condition = self.visit(node.condition)
        if condition:
            self.visit(node.body)
        elif node._elif:
            for elif_node in node._elif:
                elif_condition = self.visit(elif_node.condition)
                if elif_condition:
                    self.visit(elif_node.body)
                    break
            else:
                if node._else:
                    self.visit(node._else.body)
        else:
            if node._else:
                self.visit(node._else.body)

    @visitor.when(WhileStructureNode)
    def visit(
        self, node: WhileStructureNode, scope: Scope = None, Context: Context = None
    ):
        ret = None
        while self.visit(node.condition, scope, Context):
            for statment in node.body:
                ret = self.visit(statment, scope, Context)
        return ret

    @visitor.when(IdentifierNode)
    def visit(self, node: IdentifierNode, scope: Scope = None, Context: Context = None):
        return scope.get_variable(node.id)

    @visitor.when(ForStructureNode)
    def visit(
        self, node: ForStructureNode, scope: Scope = None, Context: Context = None
    ):
        self.visit(node.init_assigments, scope, Context)
        ret = None
        while self.visit(node.condition, scope, Context):
            for statment in node.body:
                ret = self.visit(statment, scope, Context)
            self.visit(node.increment_condition)
        return ret

    @visitor.when(BoolIsTypeNode)
    def visit(self, node: BoolIsTypeNode, scope: Scope = None, Context: Context = None):
        value = self.visit(node.left, scope, Context)
        return isinstance(value, node.right)

    @visitor.when(BoolAndNode)
    def visit(self, node: BoolAndNode, scope: Scope = None, Context: Context = None):
        left_value = self.visit(node.left, scope, Context)
        right_value = self.visit(node.right, scope, Context)
        return left_value and right_value

    @visitor.when(BoolOrNode)
    def visit(self, node: BoolOrNode, scope: Scope = None, Context: Context = None):
        left_value = self.visit(node.left, scope, Context)
        right_value = self.visit(node.right, scope, Context)
        return left_value or right_value

    @visitor.when(BoolNotNode)
    def visit(self, node: BoolNotNode, scope: Scope = None, Context: Context = None):
        value = self.visit(node.node, scope, Context)
        return not value

    @visitor.when(BoolCompLessNode)
    def visit(
        self, node: BoolCompLessNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.left, scope, Context)
        right_value = self.visit(node.right, scope, Context)
        return left_value < right_value

    @visitor.when(BoolCompGreaterNode)
    def visit(
        self, node: BoolCompGreaterNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.left, scope, Context)
        right_value = self.visit(node.right, scope, Context)
        return left_value > right_value

    @visitor.when(BooleanNode)
    def visit(self, node: BooleanNode, scope: Scope = None, Context: Context = None):
        return node.value

    @visitor.when(BoolCompLessEqualNode)
    def visit(
        self, node: BoolCompLessEqualNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.left, scope, Context)
        right_value = self.visit(node.right, scope, Context)
        return left_value <= right_value

    @visitor.when(BoolCompGreaterEqualNode)
    def visit(
        self,
        node: BoolCompGreaterEqualNode,
        scope: Scope = None,
        Context: Context = None,
    ):
        left_value = self.visit(node.left, scope, Context)
        right_value = self.visit(node.right, scope, Context)
        return left_value >= right_value

    @visitor.when(BoolCompEqualNode)
    def visit(
        self, node: BoolCompEqualNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.left, scope, Context)
        right_value = self.visit(node.right, scope, Context)
        return left_value == right_value

    @visitor.when(BoolCompNotEqualNode)
    def visit(
        self, node: BoolCompNotEqualNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value != right_value

    @visitor.when(PlusExpressionNode)
    def visit(
        self, node: PlusExpressionNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.expression_1, scope, Context)
        right_value = self.visit(node.expression_2, scope, Context)
        return left_value + right_value

    @visitor.when(SubsExpressionNode)
    def visit(
        self, node: SubsExpressionNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.expression_1, scope, Context)
        right_value = self.visit(node.expression_2, scope, Context)
        return left_value - right_value

    @visitor.when(DivExpressionNode)
    def visit(
        self, node: DivExpressionNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.expression_1, scope, Context)
        right_value = self.visit(node.expression_2, scope, Context)
        return left_value / right_value

    @visitor.when(MultExpressionNode)
    def visit(
        self, node: MultExpressionNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.expression_1, scope, Context)
        right_value = self.visit(node.expression_2, scope, Context)
        return left_value * right_value

    @visitor.when(ModExpressionNode)
    def visit(
        self, node: ModExpressionNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.expression_1, scope, Context)
        right_value = self.visit(node.expression_2, scope, Context)
        return left_value % right_value

    @visitor.when(PowExpressionNode)
    def visit(
        self, node: PowExpressionNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.expression_1, scope, Context)
        right_value = self.visit(node.expression_2, scope, Context)
        return left_value**right_value

    @visitor.when(SqrtMathNode)
    def visit(self, node: SqrtMathNode, scope: Scope = None, Context: Context = None):
        expression_value = self.visit(node.expression)
        return math.sqrt(expression_value)

    @visitor.when(SinMathNode)
    def visit(self, node: SinMathNode, scope: Scope = None, Context: Context = None):
        expression_value = self.visit(node.expression, scope, Context)
        return math.sin(expression_value)

    @visitor.when(CosMathNode)
    def visit(self, node: CosMathNode, scope: Scope = None, Context: Context = None):
        expression_value = self.visit(node.expression, scope, Context)
        return math.cos(expression_value)

    @visitor.when(TanMathNode)
    def visit(self, node: TanMathNode, scope: Scope = None, Context: Context = None):
        expression_value = self.visit(node.expression, scope, Context)
        return math.tan(expression_value)

    @visitor.when(ExpMathNode)
    def visit(self, node: ExpMathNode, scope: Scope = None, Context: Context = None):
        expression_value = self.visit(node.expression, scope, Context)
        return math.exp(expression_value)

    @visitor.when(RandomFunctionCallNode)
    def visit(
        self, node: RandomFunctionCallNode, scope: Scope = None, Context: Context = None
    ):
        return random.random()

    @visitor.when(LogFunctionCallNode)
    def visit(
        self, node: LogFunctionCallNode, scope: Scope = None, Context: Context = None
    ):
        base_value = self.visit(node.base, scope, Context)
        expression_value = self.visit(node.expression, scope, Context)
        return math.log(expression_value, base_value)

    @visitor.when(StringConcatNode)
    def visit(
        self, node: StringConcatNode, scope: Scope = None, Context: Context = None
    ):
        left_value = self.visit(node.left, scope, Context)
        right_value = self.visit(node.right, scope, Context)
        return str(left_value) + str(right_value)

    @visitor.when(StringConcatWithSpaceNode)
    def visit(
        self,
        node: StringConcatWithSpaceNode,
        scope: Scope = None,
        Context: Context = None,
    ):
        left_value = self.visit(node.left, scope, Context)
        right_value = self.visit(node.right, scope, Context)
        return str(left_value) + " " + str(right_value)
