# from AST import *

from typing import List
from src.cmp import visitor
from src.cmp.semantic import Context, SemanticError
from src.tools.ast_nodes import *


class TypeCollectorVisitor:
    def __init__(self, context: Context, errors) -> None:
        self.context: Context = context
        self.errors: List[str] = errors

    @visitor.on("node")
    def visit(self, node):
        print(f"OnGeneric: {type(node)}")
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for statment in node.statments:
            print(f"Statement (Collector): {statment}")
            self.visit(statment)

    @visitor.when(TypeDefinitionNode)
    def visit(self, node: TypeDefinitionNode):
        try:
            self.context.create_type(node.id.id)
        except:
            self.errors.append(
                SemanticError(
                    f"El nombre de tipo {node.id.id} ya ha sido tomado [L:{node.location[0]}, C:{node.location[1]}]"
                )
            )
