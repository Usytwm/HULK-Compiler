from src.cmp.semantic import Context
from src.cmp import visitor
from src.tools.ast_nodes import (
    MethodDefinitionNode,
    ProgramNode,
    TypeDefinitionNode,
)


class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = Context()
        self.errors = errors

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, context: Context):
        context.create_type("number")
        context.create_type("bool")
        context.create_type("str")

        for statments in node.statments:
            self.visit(statments, context)

    @visitor.when(TypeDefinitionNode)
    def visit(self, node: TypeDefinitionNode, context: Context):
        if context.is_defined(node.id):
            self.errors.append(
                f"El nombre {node.id} ya ha sido definido en este contexto"
            )
        else:
            context.create_type(node.id)

        child_context = context.create_child()
        for method in node.methods:
            self.visit(method, child_context)

    @visitor.when(MethodDefinitionNode)
    def visit(self, node: MethodDefinitionNode, context: Context):
        for method in node.body:
            self.visit(method, context)
