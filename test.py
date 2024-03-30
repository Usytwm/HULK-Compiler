from src.semantic_check.semantic_check import SemanticCheck
from src.cmp.evaluation import evaluate_reverse_parse
from src.syntax_analysis.LR1Parser import LR1Parser
from src.lexical_analysis.lexer import Lexer
from src.lexical_analysis.regex_patterns import build_regex
from src.syntax_analysis.grammLR1 import EOF, gramm_Hulk_LR1


# define grammar
grammar = gramm_Hulk_LR1()
text = "print(42);"

lexer = Lexer(
    build_regex(),
    EOF,
)

tokens = lexer(text)
tokentypes = [token.token_type for token in tokens]
parser = LR1Parser(grammar, True)
parser, operations = parser(tokentypes)
ast = evaluate_reverse_parse(parser, operations, tokens)
checker = SemanticCheck()
checker.semantick_check(ast)

print(ast)
