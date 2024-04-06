from src.semantic_check.interpreter import TreeWalkInterpreter
from src.cmp.semantic import Context, Method, Scope, Type
from src.semantic_check.TypeBuilder import TypeBuilderVisitor
from src.semantic_check.TypeChecker import TypeCheckerVisitor
from src.semantic_check.TypeCollector import TypeCollectorVisitor


class SemanticCheck:
    def __init__(self) -> None:
        self.context = Context()
        self.context.create_type("object")
        default_types = ["number", "string", "bool", "void", "any"]
        for type in default_types:
            self.context.create_type(type)
            self.context.get_type(type).parent = self.context.get_type("object")

        # ------------------Inicializando funciones por defecto-----------------------------------------------#
        self.scope = Scope(parent=None)

        self.default_functions = [
            "sin",
            "cos",
            "sqrt",
            "exp",
            "rand",
            "log",
            "print",
        ]
        self.errors = []

    def semantick_check(self, ast):
        type_collector = TypeCollectorVisitor(self.context, self.scope, self.errors)
        type_collector.visit(ast)

        build_collector = TypeBuilderVisitor(self.context, self.scope, self.errors)
        build_collector.visit(ast)

        semantic_checking = TypeCheckerVisitor(
            self.context, self.scope, self.errors, self.default_functions
        )
        semantic_checking.visit(ast)
        print(self.errors)
        if len(self.errors) == 0:
            interpreter = TreeWalkInterpreter()
            interpreter.visit(ast)
