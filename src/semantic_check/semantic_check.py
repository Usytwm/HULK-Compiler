from src.semantic_check.interpreter import TreeWalkInterpreter
from src.cmp.semantic import Context, Method, Scope, Type
from src.semantic_check.TypeBuilder import TypeBuilderVisitor
from src.semantic_check.TypeChecker import TypeCheckerVisitor
from src.semantic_check.TypeCollector import TypeCollectorVisitor


class SemanticCheck:
    def __init__(self) -> None:
        self.context = Context()
        self.scope = Scope()
        default_types = ["object", "string", "number", "bool", "void", "any"]
        for type in default_types:
            self.context.create_type(type)
        default_functions_only_numerical_arguments = ["sen", "cos", "sqrt", "exp"]
        for function in default_functions_only_numerical_arguments:
            self.scope.functions[function] = Method(
                function,
                ["expression"],
                [self.context.get_type("number")],
                self.context.get_type("number"),
            )

        self.scope.functions["log"] = Method(
            "log",
            ["base", "expression"],
            [self.context.get_type("number") for _ in range(2)],
            Type("number"),
        )
        self.scope.functions["print"] = Method(
            "print", ["object"], [Type("object")], self.context.get_type("void")
        )
        self.scope.functions["rand"] = Method(
            "rand", [], [], self.context.get_type("number")
        )
        self.errors = []

    def semantick_check(self, ast):
        # type_collector = TypeCollectorVisitor(self.context, self.scope, self.errors)
        # type_collector.visit(ast)

        # build_collector = TypeBuilderVisitor(self.context, self.scope, self.errors)
        # build_collector.visit(ast)

        # semantic_checking = TypeCheckerVisitor(
        #     self.context, self.scope, self.errors, self.scope.functions
        # )
        # semantic_checking.visit(ast)

        if len(self.errors) == 0:
            interpreter = TreeWalkInterpreter()
            interpreter.visit(ast)
