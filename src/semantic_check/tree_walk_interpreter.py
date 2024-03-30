import math
import random
from src.tools.ast_nodes import *
from src.cmp.semantic import *
import src.cmp.visitor as visitor


class TreeWalkInterpreter:

    def __init__(self):
        self.context = Context()
        self.scope = Scope()
        self.errors = []

    @visitor.on("node")
    def visit(self, node, tabs):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for statement in node.statments:
            self.visit(statement)

    @visitor.when(PrintStatmentNode)
    def visit(self, node: PrintStatmentNode):
        value = self.visit(node.expression)
        print(value)

    @visitor.when(NumberNode)
    def visit(self, node: NumberNode):
        return node.value

    @visitor.when(FunctionDefinitionNode)
    def visit(self, node: FunctionDefinitionNode):
        # Crear un objeto Method para la función.
        method = Method(
            node.id,
            [param.items[0].key for param in node.parameters],
            [self.context.get_type(param.items[0].value) for param in node.parameters],
            self.context.get_type(node.type_annotation),
        )

        # Aquí asumimos que todas las funciones pertenecen a un tipo global o algo similar.
        # Necesitarías ajustar esto según cómo estés manejando los tipos y dónde deben almacenarse las funciones.
        global_type = self.context.get_type(
            "Global"
        )  # Suponiendo que tienes un tipo global o similar.
        global_type.define_method(
            node.id,
            [param["name"] for param in node.parameters],
            [self.context.get_type(param["type"]) for param in node.parameters],
            self.context.get_type(node.type_annotation),
        )

        self.visit(node.body)

    @visitor.when(FunctionCallNode)
    def visit(node: FunctionCallNode):
        pass

    @visitor.when(IfStructureNode)
    def visit(self, node: IfStructureNode):
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
    def visit(self, node: WhileStructureNode):
        while self.visit(node.condition):
            self.visit(node.body)

    @visitor.when(ForStructureNode)
    def visit(self, node: ForStructureNode):
        for init_assignment in node.init_assigments:
            self.visit(init_assignment)
        while self.visit(node.condition):
            self.visit(node.body)
            for increment_assignment in node.increment_condition:
                self.visit(increment_assignment)
        # NO LO TENGO CLARO

    @visitor.when(BoolIsTypeNode)
    def visit(self, node: BoolIsTypeNode):
        value = self.visit(node.expression)
        return isinstance(value, node.type)

    @visitor.when(BoolAndNode)
    def visit(self, node: BoolAndNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value and right_value

    @visitor.when(BoolOrNode)
    def visit(self, node: BoolOrNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value or right_value

    @visitor.when(BoolNotNode)
    def visit(self, node: BoolNotNode):
        value = self.visit(node.expression)
        return not value

    @visitor.when(BoolCompLessNode)
    def visit(self, node: BoolCompLessNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value < right_value

    @visitor.when(BoolCompGreaterNode)
    def visit(self, node: BoolCompGreaterNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value > right_value

    @visitor.when(BoolCompLessEqualNode)
    def visit(self, node: BoolCompLessEqualNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value <= right_value

    @visitor.when(BoolCompGreaterEqualNode)
    def visit(self, node: BoolCompGreaterEqualNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value >= right_value

    @visitor.when(BoolCompEqualNode)
    def visit(self, node: BoolCompEqualNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value == right_value

    @visitor.when(BoolCompNotEqualNode)
    def visit(self, node: BoolCompNotEqualNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value != right_value

    @visitor.when(PlusExpressionNode)
    def visit(self, node: PlusExpressionNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value + right_value

    @visitor.when(SubsExpressionNode)
    def visit(self, node: SubsExpressionNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value - right_value

    @visitor.when(DivExpressionNode)
    def visit(self, node: DivExpressionNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value / right_value

    @visitor.when(MultExpressionNode)
    def visit(self, node: MultExpressionNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value * right_value

    @visitor.when(ModExpressionNode)
    def visit(self, node: ModExpressionNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value % right_value

    @visitor.when(PowExpressionNode)
    def visit(self, node: PowExpressionNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return left_value**right_value

    @visitor.when(SqrtMathNode)
    def visit(self, node: SqrtMathNode):
        expression_value = self.visit(node.expression)
        return math.sqrt(expression_value)

    @visitor.when(SinMathNode)
    def visit(self, node: SinMathNode):
        expression_value = self.visit(node.expression)
        return math.sin(expression_value)

    @visitor.when(CosMathNode)
    def visit(self, node: CosMathNode):
        expression_value = self.visit(node.expression)
        return math.cos(expression_value)

    @visitor.when(TanMathNode)
    def visit(self, node: TanMathNode):
        expression_value = self.visit(node.expression)
        return math.tan(expression_value)

    @visitor.when(ExpMathNode)
    def visit(self, node: ExpMathNode):
        expression_value = self.visit(node.expression)
        return math.exp(expression_value)

    @visitor.when(RandomCallNode)
    def visit(self, node: RandomCallNode):
        return random.random()

    @visitor.when(LogCallNode)
    def visit(self, node: LogCallNode):
        base_value = self.visit(node.base)
        expression_value = self.visit(node.expression)

    @visitor.when(StringConcatNode)
    def visit(self, node: StringConcatNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return str(left_value) + str(right_value)

    @visitor.when(StringConcatWithSpaceNode)
    def visit(self, node: StringConcatWithSpaceNode):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        return str(left_value) + " " + str(right_value)
