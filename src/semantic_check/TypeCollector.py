from src.cmp.semantic import Context, Method, Scope, SemanticError
import src.cmp.visitor as visitor
from src.tools.ast_nodes import *


class TypeCollectorVisitor:
    def __init__(self, contetx: Context, scope: Scope, errors: List[str]) -> None:
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
    def visit(self, node: TypeDefinitionNode):
        try:
            self.context.create_type(node.id)
        except:
            self.errors.append(
                SemanticError(f"El nombre de tipo {node.id} ya ha sido tomado")
            )

    @visitor.when(FunctionDefinitionNode)
    def visit(self, node: FunctionDefinitionNode):
        try:
            self.scope.functions[node.id]
            self.errors.append(
                SemanticError(f"El nombre de tipo {node.id} ya ha sido tomado")
            )
        except:
            self.scope.functions[node.id] = []
