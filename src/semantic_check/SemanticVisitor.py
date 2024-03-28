from cmp.cil import ProgramNode
from cmp.semantic import Scope
import src.cmp.visitor as visitor
from AST.Nodes import *
from AST.Context import *
from defined import *


class SemanticCheckerVisitor(object):
    def __init__(self):
        self.errors = []
        self.scope = Scope

    @visitor.on("node")
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope=None):
        scope = node.scope
        ans = []

    @visitor.when(VarDeclarationNode)
    def visit(self, node, scope):
        if scope.is_var_defined(node.idx):
            self.errors.append(f"The variable {node.idx} exists")
        # else: scope.define_variable(node.idx)
        self.visit(node.expr, scope)
        return

    @visitor.when(GetNode)
    def visit(self, node, context):
        if not context.is_var_defined(node.var):  # Si la variable no esta definida
            self.errors.append(f"The variable {node.var} does not exists ")
        elif not hasattr(
            context.get_local_variable_info(node.var), node.attr
        ):  # Verifica si la variable contiene ese atributo o propiedad
            self.errors.append(
                f" The variable {node.attr} does not contain the attribute {self.attr} "
            )  # Si la variable no contiene esa propiedad

        return

    @visitor.when(SetNode)
    def visit(self, node, context):
        if not context.is_var_defined(node.var):  # Si la variable no esta definida
            self.errors.append(f"The variable {node.var} does not exists ")
        elif not hasattr(
            context.get_local_variable_info(node.var), node.attr
        ):  # Verifica si la variable contiene ese atributo o propiedad
            self.errors.append(
                f" The variable {node.attr} does not contain the attribute {self.attr} "
            )  # Si la variable no contiene esa propiedad

        return

    @visitor.when(AddRemoveNode)
    def visit(self, node, context):
        if not context.is_var_defined(node.name_patient):
            self.errors.append(f"Patient {node.name_patient} does not exists ")
        if node.func != "add" and node.func != "remove":
            self.errors.append(
                f"Patient {node.name_patient} does not contain a {node.func} "
            )

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        if scope.check_func_defined(node.idx, len(node.params)):
            self.errors.append(f"The feature {node.idx} alredy exists")
        else:
            scope.define_function(node)

        innerContext = scope.create_child_scope()
        for arg in node.params:
            innerContext.define_variable(arg[0], " ", arg[1])
        for i in node.stat_list:
            self.visit(i, innerContext)
        return

    @visitor.when(ReturnNode)
    def visit(self, node, scope):
        self.visit(node.expr, scope)
        return

    @visitor.when(PrintNode)
    def visit(self, node, scope):
        self.visit(node.expr, scope)
        return

    @visitor.when(PatientNode)
    def visit(self, node, scope):
        if scope.is_var_defined(node.name):
            self.errors.append(f"The variable {node.name} exists")
        return

    @visitor.when(RedefVarDeclarationNode)
    def visit(self, node, scope):
        if not scope.is_var_defined(node.idx):
            self.errors.append(f"The variable {node.idx} does not exist")
        return

    @visitor.when(ForNode)
    def visit(self, node, context):
        if node.idx != node.idx_counter:
            self.errors.append(f"The id {node.idx} must be equal to {node.idx_counter}")
        if node.counter_one != node.counter_two:
            self.errors.append(
                f"The id {node.counter_one} must be equal to {node.counter_two}"
            )
        child = context.create_child_context()
        child.def_var(node.idx, node.idx_value)
        for i in node.body:
            self.visit(i, child)

    @visitor.when(IfExprNode)
    def visit(self, node, context):
        self.visit(node.expr)
        for i in node.body:
            self.visit(i, context)

    @visitor.when(IfElseExprNode)
    def visit(self, node, context):
        self.visit(node.expr)
        for i in node.one_body:
            self.visit(i, context)
        for i in node.two_body:
            self.visit(i, context)

    @visitor.when(CallNode)
    def visit(self, node, scope):
        if not scope.check_func_defined(node.idx, len(node.args)):
            self.errors.append(
                f"The feature {node.idx} does not exist with {len(node.args)} arguments"
            )
        # for arg in node.args:
        #     self.visit(arg,scope)
        return

    @visitor.when(VariableNode)
    def visit(self, node, scope):
        if not scope.is_var_defined(node.value):
            self.errors.append(f"The variable {node.value} does not exists")
        return

    @visitor.when(AtomicNode)
    def visit(self, node, scope):
        return

    @visitor.when(BinaryNode)
    def visit(self, node, scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return

    @visitor.when(LeqNode)
    def visit(self, node, scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return

    @visitor.when(LeqNode)
    def visit(self, node, scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return

    @visitor.when(GeqNode)
    def visit(self, node, scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return

    @visitor.when(NotNode)
    def visit(self, node, scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return

    @visitor.when(LessNode)
    def visit(self, node, scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return

    @visitor.when(GreaterNode)
    def visit(self, node, scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return

    @visitor.when(FindNode)
    def visit(self, node, scope):
        if not scope.is_var_defined(node.patient):
            self.errors.append(f"The variable {node.patient} does not exist")
        elif not isinstance(scope.get_local_variable_info(node.patient), Patient()):
            self.errors.append(f"The type of {node.patient} does not correct")
        return

    @visitor.when(CancerNode)
    def visit(self, node, scope):
        if not scope.is_var_defined(node.patient):
            self.errors.append(f"The variable {node.patient} does not exist")
        elif not isinstance(scope.get_local_variable_info(node.patient), Patient()):
            self.errors.append(f"The type of {node.patient} does not correct")
        if (
            node.cancer != "BreastCancer"
            and node.cancer != "OvarianCancer"
            and node.cancer != "PancreaticCancer"
        ):
            self.errors.append(f"{node.cancer} no existe")

        return

    # @visitor.when(ListExprNode)
    # def visit(self, node, scope):
    #     return
