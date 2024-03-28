from cmp.semantic import Scope
from semantic_check.TypeCollector import TypeCollector
import src.cmp.visitor as visitor
from tools.ast_nodes import *


class SemanticCheckerVisitor(object):
    def __init__(self):
        self.errors = []
        self.scope = Scope

    @visitor.on("node")
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope: Scope):

        typeCollector = TypeCollector(errors=self.errors)
        typeCollector.visit(node)

        for statment in node.statments:
            self.visit(statment, scope)

    @visitor.when(PrintStatmentNode)
    def visit(self, node: PrintStatmentNode, scope: Scope):
        self.visit(node.expression, scope)

    @visitor.when(LetNode)
    def visit(self, node: LetNode, scope: Scope):
        if scope.is_defined(node.id):
            self.errors.append(f"El nombre {node.id} ya ha sido definido en este Scope")
        self.visit(node.expression, scope)

    @visitor.when(KernAssigmentNode)
    def visit(self, node: KernAssigmentNode, scope: Scope):
        if not scope.is_defined(node.id):
            self.errors.append(f"El nombre {node.id} no ha sido definido en este Scope")
        self.visit(node.expression, scope)

    @visitor.when(MethodDefinitionNode)
    def visit(self, node: MethodDefinitionNode, scope: Scope):
        try:
            args_len = scope.functions[node.id]
            current_args_len = len(node.parameters)
            if current_args_len in args_len:
                self.errors.append(f"La función {node.id} ya sta definida")
            else:
                scope.functions[node.id].append(current_args_len)

        except:
            scope.functions[node.id].append(len(node.parameters))
        child_scope = scope.create_child()
        for vname, vtype in node.parameters:
            child_scope.define_variable(vname, vtype)

        for statment in node.body:
            self.visit(statment, child_scope)

    @visitor.when(IfStructureNode)
    def visit(self, node: IfStructureNode, scope: Scope):
        self.visit(node.expresion, scope)
        child_scope = scope.create_child()
        for statment in node.body:
            self.visit(statment, child_scope)
        self.visit(node._elif, scope)
        self.visit(node._elif, scope)

    @visitor.when(ElifStructureNode)
    def visit(self, node: ElifStructureNode, scope: Scope):
        self.visit(node.expresion, scope)
        child_scope = scope.create_child()
        for statment in node.body:
            self.visit(statment, child_scope)

    @visitor.when(ElseStructureNode)
    def visit(self, node: ElseStructureNode, scope: Scope):
        child_scope = scope.create_child()
        for statment in node.body:
            self.visit(statment, child_scope)

    @visitor.when(WhileStructureNode)
    def visit(self, node: WhileStructureNode, scope: Scope):
        child_scope = scope.create_child()
        self.visit(node.expresion, child_scope)
        for statment in node.body:
            self.visit(statment, child_scope)

    @visitor.when(ForStructureNode)
    def visit(self, node: ForStructureNode, scope: Scope):
        for assigments in node.init_assigments:
            self.visit(assigments, scope)

        self.visit(node.expression, scope)
        self.visit(node.increment_condition, scope)
        child = scope.create_child()
        for statment in node.body:
            self.visit(statment, child)

    @visitor.when(TypeDefinitionNode)
    def visit(self, node: TypeDefinitionNode, scope: Scope):
        child_type = scope.create_child()
        for vname, vtype in node.parameters:
            child_type.define_variable(vname, vtype)

        for vname in node.attribute:
            child_type.define_variable(vname, "object")

        for method in node.methods:
            self.visit(method, child_type)
