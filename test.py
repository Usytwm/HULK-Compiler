from src.semantic_check.semantic_check import SemanticCheck
from src.cmp.evaluation import evaluate_reverse_parse
from src.syntax_analysis.LR1Parser import LR1Parser
from src.lexical_analysis.lexer import Lexer
from src.lexical_analysis.regex_patterns import build_regex
from src.syntax_analysis.grammLR1 import EOF, gramm_Hulk_LR1

path = "test/Data/prueba.txt"
with open(path, "r", encoding="utf-8") as archivo:
    content = archivo.read()

# define grammar
grammar = gramm_Hulk_LR1()
text = """
let a = 5, b = 10, c = 20 in {
    print(a+b);
    print(b*c);
    print(c/a);
};"""

lexer = Lexer(
    build_regex(),
    EOF,
)

tokens = lexer(content)
tokentypes = [token.token_type for token in tokens]
parser = LR1Parser(grammar)
parser, operations = parser(tokentypes)
ast = evaluate_reverse_parse(parser, operations, tokens)
checker = SemanticCheck()
checker.semantick_check(ast)

# print(ast)
from semantic_check.interpreter import TreeWalkInterpreter
from src.cmp.semantic import Context, Scope
from src.semantic_check.TypeBuilder import TypeBuilderVisitor
from src.semantic_check.TypeChecker import TypeCheckerVisitor
from src.semantic_check.TypeCollector import TypeCollectorVisitor
from src.tools.ast_nodes import *


# class SemanticCheckingVisitor:
#     def __init__(self) -> None:
#         # ------------------Inicializando tipos por defecto---------------------------------------------------#
#         self.context = Context()
#         default_types = ["object", "number", "string", "bool", "void"]
#         for type in default_types:
#             self.context.create_type(type)

#         # print(f'Context: {[item for item in self.context.types.keys()]}')

#         # ------------------Inicializando funciones por defecto-----------------------------------------------#
#         self.scope = Scope(parent=None)

#         # TODO Se puedo no poner estas funciones como definidas y desde la gramatica crear un SqrNode() y luego acceder a el
#         self.default_functions = ["sen", "cos", "sqrt", "exp"]
#         # for func in self.default_functions:
#         #     self.scope.functions[func] = Method(func, ['expression'], [self.context.get_type('number')], self.context.get_type('number'))

#         self.default_functions.extend(["rand", "log", "print"])
#         # self.scope.functions['rand'] = [Method(func, [], [], self.context.get_type('number'))]
#         # self.scope.functions['log'] = [Method(func, ['base', 'expression'], [self.context.get_type('number'), self.context.get_type('number')], self.context.get_type('number'))]
#         # self.scope.functions['print'] = [Method(func, ['expression'], [self.context.get_type('object')], self.context.get_type('string'))]

#         # ----------------------------------------------------------------------------------------------------#
#         self.errors = []

#     # TODO Pasar a los collectors copias de context scope y errors
#     def semantic_checking(self, ast):
#         type_collector = TypeCollectorVisitor(self.context, self.scope, self.errors)
#         type_collector.visit(ast)

#         type_builder = TypeBuilderVisitor(self.context, self.scope, self.errors)
#         type_builder.visit(ast)

#         type_checker = TypeCheckerVisitor(
#             self.context, self.scope, self.errors, self.default_functions
#         )
#         type_checker.visit(ast)

#         # print('Context')
#         # for name, type in self.context.types.items():
#         #     print(f'Type: {name}')
#         #     print(f'attributes: {type.attributes}')
#         #     print(f'attributes: {type.methods}')

#         return self.errors


ast0 = ProgramNode([NumberNode(42)])
ast1 = ProgramNode([PrintStatmentNode(NumberNode(42))])
ast2 = ProgramNode(
    [
        PrintStatmentNode(
            DivExpressionNode(
                MultExpressionNode(
                    PowExpressionNode(
                        PlusExpressionNode(NumberNode(1), NumberNode(2)), NumberNode(3)
                    ),
                    NumberNode(4),
                ),
                NumberNode(5),
            )
        )
    ]
)
ast3 = ProgramNode([PrintStatmentNode(StringNode("Hello World"))])
ast4 = ProgramNode(
    [
        PrintStatmentNode(
            StringNode(
                StringConcatWithSpaceNode(
                    StringNode("The meaning of life is"), NumberNode(42)
                )
            )
        )
    ]
)
ast5 = ProgramNode(
    [
        PrintStatmentNode(
            PlusExpressionNode(
                PowExpressionNode(
                    SinMathNode(MultExpressionNode(NumberNode(2), PINode())),
                    NumberNode(2),
                ),
                CosMathNode(
                    DivExpressionNode(
                        MultExpressionNode(NumberNode(3), PINode()),
                        LogCallNode(NumberNode(4), NumberNode(64)),
                    )
                ),
            )
        )
    ]
)
ast6 = ProgramNode(
    [
        PrintStatmentNode(NumberNode(45)),
        TypeDefinitionNode(
            id="Point",
            parameters=[],
            inheritance=TypeNode("object"),
            attributes=[
                KernAssigmentNode("x", TypeNode("number")),
            ],
            methods=[
                FunctionDefinitionNode(
                    "setX",
                    TypeNode("number"),
                    [],
                    PlusExpressionNode(NumberNode(4), NumberNode(5)),
                )
            ],
        ),
        FunctionDefinitionNode(
            "global_func",
            TypeNode("Point"),
            [],
            PlusExpressionNode(NumberNode(4), NumberNode(5)),
        ),
        SqrtMathNode(NumberNode(4)),
    ]
)

print_aritmetic_tests = [ast0, ast1, ast2, ast3, ast4, ast5, ast6]
for index_test in range(len(print_aritmetic_tests)):
    print(f"Test - {index_test}")
    checker = TreeWalkInterpreter()
    checker.visit(print_aritmetic_tests[index_test])
