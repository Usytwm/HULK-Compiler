from src.syntax_analysis.LR1Parser import LR1Parser
from src.lexical_analysis.lexer import Lexer
from src.lexical_analysis.regex_patterns import build_regex
from src.syntax_analysis.grammLR1 import gramm_Hulk_LR1

errors = []


# define grammar
grammar = gramm_Hulk_LR1()

text = 'x = hola => print ( "Hola Mundo" ) \n \t x=8;'


lexer = Lexer(
    build_regex(),
    "eof",
)


tokens = lexer(text)
print(tokens)
tokentypes = [token.token_type for token in tokens]
print(tokentypes)
parser = LR1Parser(grammar)

derivation = parser(tokentypes)
print(derivation)
