from cmp.semantic import Context, SemanticError
from cmp.visitor import visitor
from tools.ast_nodes import *

class TypeCollectorVisitor:
    def __init__(self, contetx, errors) -> None:
        self.context = contetx
        self.errors = errors
        
    @visitor.on('node')
    def visit(self, node, context):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, context: Context):
        
        for statment in node.statments:
            self.visit(statment, context)
            
    @visitor.when(TypeDefinitionNode)
    def visit(self, node: TypeDefinitionNode, context: Context):
        if context.is_defined(node.id):
            self.errors.append(SemanticError(f'El nombre de tipo {node.id} ya ha sido tomado'))
        else:
            context.create_type(node.id)
            
        for method in node.methods:
            inner_context = context.create_child(context)
            self.visit(method, inner_context)
            
    @visitor.when(FunctionDefinitionNode)
    def visit(self, node: FunctionDefinitionNode, context: Context):
        for statment in node.body:
            self.visit(statment, context)
            
    