from src.syntax_analysis.LR1Parser import LR1Parser
from src.lexical_analysis.lexer import Lexer
from src.lexical_analysis.regex_patterns import build_regex
from src.syntax_analysis.grammar_LR1 import gramm_Hulk_LR1
errors = []


# define grammar
grammar= gramm_Hulk_LR1()

text = 'let msg = \"Hello World\" in print(msg);'


lexer = Lexer(
            build_regex(),
            "eof",
        )

tokens = lexer(text)
print(tokens)
print("result_tokens")
tokentypes = [token.token_type for token in tokens if token.token_type != 'space']
print(tokentypes)
parser = LR1Parser(grammar)
derivation = parser(tokentypes) #Tacto  Exception: Aborting parsing, item is not viable.
#print(derivation)

#[let: let, space:  , identifier: msg, space:  , =: =, space:  , string: "Hello World", space:  , in: in, space:  , print: print, (: (, identifier: msg, ): ), ;: ;, $: $]
#[let: let, id: msg, assign: =, lit: "Hello World", in: in, print: print, opar: (, id: msg, cpar: ), semicolon: ;, eof: $]