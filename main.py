from src.semantic_check.semantic_check import SemanticCheck
from src.cmp.evaluation import evaluate_reverse_parse
from src.syntax_analysis.LR1Parser import LR1Parser
from src.lexical_analysis.lexer import Lexer
from src.lexical_analysis.regex_patterns import build_regex
from src.syntax_analysis.grammLR1 import EOF, gramm_Hulk_LR1
from src.semantic_check.interpreter import TreeInterpreter
import unittest


class TestHulk(unittest.TestCase):
    path = "test/Data/archivo.hulk"
    with open(path, "r", encoding="utf-8") as archivo:
        content = archivo.read()

    grammar = gramm_Hulk_LR1()

    lexer = Lexer(
        build_regex(),
        EOF,
    )

    parser = LR1Parser(grammar)
    checker = SemanticCheck()

    # --------------------------------Análisis Léxico--------------------------------

    tokens = lexer(content)
    tokentypes = [token.token_type for token in tokens]

    # ------------------------------Análisis Sintáctico------------------------------

    parser, operations = parser(tokentypes)

    ast = evaluate_reverse_parse(parser, operations, tokens)

    # ------------------------------Análisis Semántico------------------------------

    checker.semantic_check(ast)

    interprete = TreeInterpreter(checker.context)
    interprete.visit(ast)


if __name__ == "__main__":
    unittest.main()
