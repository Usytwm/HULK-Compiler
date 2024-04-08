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


# define grammar
grammar = gramm_Hulk_LR1()
text = """for (let x=0; x < 10; x:= x + 1){
    print(x);
} 
"""

lexer = Lexer(
    build_regex(),
    EOF,
)

tokens = lexer(text)
tokentypes = [token.token_type for token in tokens]
print(tokentypes)
parser = LR1Parser(grammar)
parser, operations = parser(tokentypes)
ast = evaluate_reverse_parse(parser, operations, tokens)
checker = SemanticCheck()
checker.semantic_check(ast)
