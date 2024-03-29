from cmp.semantic import Context, Method, Scope, SemanticError
from src.cmp.visitor import visitor
from tools.ast_nodes import *


class TypeCollectorVisitor:
    def __init__(self, contetx: Context, scope: Scope, errors) -> None:
        self.context = contetx
        self.scope = scope
        self.errors = errors

    @visitor.on("node")
    def visit(self, node, context):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):

        for statment in node.statments:
            self.visit(statment, self.context, self.scope)

    @visitor.when(TypeDefinitionNode)
    def visit(self, node: TypeDefinitionNode, context: Context, scope: Scope):
        try:
            context.create_type(node.id)
        except:
            self.errors.append(
                SemanticError(f"El nombre de tipo {node.id} ya ha sido tomado")
            )

    @visitor.when(FunctionDefinitionNode)
    def visit(self, node: FunctionDefinitionNode, context: Context, scope: Scope):
        try:
            x = scope.functions[node.id]
            self.errors.append(
                SemanticError(f"El nombre de tipo {node.id} ya ha sido tomado")
            )
        except:
            scope.functions[node.id] = []
