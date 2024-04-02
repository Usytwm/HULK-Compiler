from src.semantic_check.semantic_check import SemanticCheck
from src.cmp.evaluation import evaluate_reverse_parse
from src.syntax_analysis.LR1Parser import LR1Parser
from src.lexical_analysis.lexer import Lexer
from src.lexical_analysis.regex_patterns import build_regex
from src.syntax_analysis.grammLR1 import EOF, gramm_Hulk_LR1
from src.tools.ast_nodes import *

pathhulk = "test/Data/archivo.hulk"
with open(pathhulk, "r", encoding="utf-8") as archivo:
    contenthulk = archivo.read()
path = "test/Data/prueba.txt"
with open(path, "r", encoding="utf-8") as archivo:
    content = archivo.read()

# # define grammar
# grammar = gramm_Hulk_LR1()
# text = """
# let a = 5, b = 10, c = 20 in {
#     print(a+b);
#     print(b*c);
#     print(c/a);
# };"""

# lexer = Lexer(
#     build_regex(),
#     EOF,
# )

# tokens = lexer(contenthulk)
# tokentypes = [token.token_type for token in tokens]
# parser = LR1Parser(grammar)
# parser, operations = parser(tokentypes)
# ast = evaluate_reverse_parse(parser, operations, tokens)
# checker = SemanticCheck()
# checker.semantick_check(ast)


ast0 = ProgramNode(
    [
        KernAssigmentNode(IdentifierNode("x"), NumberNode(0)),
        PrintStatmentNode(IdentifierNode("x")),
        ForStructureNode(
            [KernAssigmentNode(IdentifierNode("i"), NumberNode(0))],
            BoolCompLessEqualNode(IdentifierNode("i"), NumberNode(10)),
            [
                DestroyNode(
                    IdentifierNode("i"),
                    PlusExpressionNode(IdentifierNode("i"), NumberNode(1)),
                )
            ],
            [
                ForStructureNode(
                    [KernAssigmentNode(IdentifierNode("j"), NumberNode(0))],
                    BoolCompLessEqualNode(IdentifierNode("j"), NumberNode(10)),
                    [
                        DestroyNode(
                            IdentifierNode("j"),
                            PlusExpressionNode(IdentifierNode("j"), NumberNode(1)),
                        )
                    ],
                    [
                        DestroyNode(
                            IdentifierNode("x"),
                            PlusExpressionNode(IdentifierNode("x"), NumberNode(1)),
                        ),
                        PrintStatmentNode(IdentifierNode("x")),
                    ],
                ),
            ],
        ),
    ]
)
# ast1 = ProgramNode([PrintStatmentNode(NumberNode(42))])
# ast2 = ProgramNode(
#     [
#         PrintStatmentNode(
#             DivExpressionNode(
#                 MultExpressionNode(
#                     PowExpressionNode(
#                         PlusExpressionNode(NumberNode(1), NumberNode(2)), NumberNode(3)
#                     ),
#                     NumberNode(4),
#                 ),
#                 NumberNode(5),
#             )
#         )
#     ]
# )
# ast3 = ProgramNode([PrintStatmentNode(StringNode("Hello World"))])
# ast4 = ProgramNode(
#     [
#         PrintStatmentNode(
#             StringConcatWithSpaceNode(
#                 StringNode("The meaning of life is"), NumberNode(42)
#             )
#         )
#     ]
# )
# ast5 = ProgramNode(
#     [
#         PrintStatmentNode(
#             PlusExpressionNode(
#                 PowExpressionNode(
#                     SinMathNode(MultExpressionNode(NumberNode(2), PINode())),
#                     NumberNode(2),
#                 ),
#                 CosMathNode(
#                     DivExpressionNode(
#                         MultExpressionNode(NumberNode(3), PINode()),
#                         LogCallNode(NumberNode(4), NumberNode(64)),
#                     )
#                 ),
#             )
#         )
#     ]
# )
# ast6 = ProgramNode(
#     [
#         PrintStatmentNode(NumberNode(45)),
#         TypeDefinitionNode(
#             id="Point",
#             parameters=[],
#             inheritance=TypeNode("object"),
#             attributes=[
#                 KernAssigmentNode("x", TypeNode("number")),
#             ],
#             methods=[
#                 FunctionDefinitionNode(
#                     "setX",
#                     TypeNode("number"),
#                     [],
#                     PlusExpressionNode(NumberNode(4), NumberNode(5)),
#                 )
#             ],
#         ),
#         FunctionDefinitionNode(
#             "global_func",
#             TypeNode("Point"),
#             [],
#             PlusExpressionNode(NumberNode(4), NumberNode(5)),
#         ),
#         SqrtMathNode(NumberNode(4)),
#     ]
# )

print_aritmetic_tests = [ast0]
for index_test in range(len(print_aritmetic_tests)):
    print(f"Test - {index_test}")
    checker = SemanticCheck()
    checker.semantick_check(print_aritmetic_tests[index_test])
