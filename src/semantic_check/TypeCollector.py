from src.cmp.semantic import Context, Method, Scope, SemanticError
import src.cmp.visitor as visitor
from src.tools.ast_nodes import *


class TypeCollectorVisitor:
    def __init__(self, context: Context, scope: Scope, errors) -> None:
        self.context: Context = context
        self.scope: Scope = scope
        self.errors: List[str] = errors

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for statment in node.statments:
            self.visit(statment)

    @visitor.when(TypeDefinitionNode)
    def visit(self, node: TypeDefinitionNode):
        try:
            InheritanceType = self.context.get_type(node.inheritance.type.id)
        except:
            self.errors.append(
                SemanticError(
                    f"No es posible heredar de {node.inheritance.type.id} porque no esta definido"
                )
            )
        try:
            self.context.create_type(node.id.id)
        except:
            self.errors.append(
                SemanticError(f"El nombre de tipo {node.id.id} ya ha sido tomado")
            )

    @visitor.when(FunctionDefinitionNode)
    def visit(self, node: FunctionDefinitionNode):
        if not node.id.id in self.scope.functions:
            self.scope.functions[node.id.id] = []
        else:
            self.errors.append(SystemError(f"El metodo {node.id.id} ya existe"))

    @visitor.when(CollectionNode)
    def visit(self, node: CollectionNode):
        for element in node.collection:
            self.visit(element)
