from src.cmp.semantic import Context, Method, Scope, Type
from src.semantic_check.TypeBuilder import TypeBuilderVisitor
from src.semantic_check.TypeChecker import TypeCheckerVisitor
from src.semantic_check.TypeCollector import TypeCollectorVisitor


class SemanticCheck:
    def __init__(self) -> None:
        # ------------------Inicializando tipos por defecto---------------------------------------------------#
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
            "tan",
            "rand",
            "log",
            "print",
        ]
        self.errors = []

    def semantic_check(self, ast):
        type_collector = TypeCollectorVisitor(self.context, self.errors)
        type_collector.visit(ast)

        type_builder = TypeBuilderVisitor(self.context, self.scope, self.errors)
        type_builder.visit(ast)

        type_checker = TypeCheckerVisitor(
            self.context, self.scope, self.errors, self.default_functions
        )
        type_checker.visit(ast)

        return self.errors
