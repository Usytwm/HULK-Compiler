import sys
import os

current_dir = os.getcwd()
sys.path.insert(0, current_dir)

from src.lexical_analysis.regular_expressions import Regex
from src.cmp.automata import (
    State,
)
from src.cmp.utils import Token


class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()

    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            # Your code here!!!
            automaton, states = State.from_nfa(Regex(regex).automaton, get_states=True)

            for state in states:
                if state.final:
                    state.tag = (n, token_type)

            regexs.append(automaton)
        return regexs

    def _build_automaton(self):
        start = State("start")
        # Your code here!!!
        for state in self.regexs:
            start.add_epsilon_transition(state)

        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        lex = ""

        for symbol in string:
            # Your code here!!!
            if state.has_transition(symbol):
                lex += symbol
                state = state[symbol][0]

                if state.final:
                    final = state
                    final.lex = lex
            else:
                break

        if final:
            return final, final.lex

        return None, None

    def _tokenize(self, text):
        # Your code here!!!
        while text:
            final, lex = self._walk(text)

            assert final, "Unexpected token nearby: " + text[:10]

            text = text[len(lex) :]

            final = [state.tag for state in final.state if state.tag]
            final.sort()

            yield lex, final[0][1]

        yield "$", self.eof

    def __call__(self, text):
        return [Token(lex, ttype) for lex, ttype in self._tokenize(text)]


nonzero_digits = "|".join(str(n) for n in range(1, 10))
letters = "|".join(chr(n) for n in range(ord("a"), ord("z") + 1))

print("Non-zero digits:", nonzero_digits)
print("Letters:", letters)

lexer = Lexer(
    [
        # Paréntesis y delimitadores
        ("num", "\-?(0|[1-9][0-9]*)(\.[0-9]+)?"),
        ("opar", "\("),
        ("cpar", "\)"),
        ("plus", "\+"),
        ("minus", "\-"),
        ("star", "\*"),
        ("div", "\/"),
        ("lbrace", "\{"),
        ("rbrace", "\}"),
        ("semicolon", ";"),
        ("comma", ","),
        ("range", "range"),
        # Operadores de asignación y definición
        ("assign", "="),
        ("def", ":="),
        ("type", ":"),
        ("dot", "\."),
        ("underscore", "_"),
        ("pipe", "\|"),
        # Operadores de comparación
        ("lt", "<"),
        ("le", "<="),
        ("gt", ">"),
        ("ge", ">="),
        ("eq", "=="),
        ("ne", "!="),
        # Números (enteros y decimales)
        # ("num", "(0|[1-9][0-9]*)(\.[0-9]+)?"),
        # Palabras clave
        ("print", "print"),
        ("if", "if"),
        ("else", "else"),
        ("let", "let"),
        ("in", "in"),
        ("for", "for"),
        ("function", "function"),
        ("type", "type"),
        # Identificadores
        ("id", "[a-zA-Z_][a-zA-Z0-9_]*"),
        # Cadenas de texto (incluyendo caracteres especiales)
        ("string", '\\"[a-zA-Z0-9_: ]*\\"'),
        # Espacios (para ser ignorados o manejados específicamente)
        ("space", " *"),
        # Nueva línea
        ("newline", "\n"),
        # Otros tokens especiales (como el operador de concatenación @)
        ("concat", "@"),
        # Funciones matemáticas y constantes
        ("math_func", "(sin|cos|tan|log|sqrt)"),
        ("pi", "PI"),
    ],
    "eof",
)

text = 'let a = - 5.879 0.98789 -0.998 in {\n    print(a);\n    print("Calculating:");\n    let result = (a + 3) * 7;\n    print(result);\n    if (result > 35) {\n        print("Result is greater than 35");\n    } else {\n        print("Result is 35 or less");\n    }\n    for (i in range(0, 10)) {\n        print(i);\n    }\n    let piValue = PI;\n    print(sin(piValue / 2));\n}'

print(f'\n>>> Tokenizando: "{text}"')
tokens = lexer(text)
print(tokens)
assert [t.token_type for t in tokens] == [
    "num",
    "space",
    "for",
    "space",
    "num",
    "foreach",
    "space",
    "id",
    "eof",
]
assert [t.lex for t in tokens] == [
    "5465",
    " ",
    "for",
    " ",
    "45",
    "foreach",
    " ",
    "fore",
    "$",
]

text = "_4forense for_foreach for4foreach _foreach foreach foreachk ifelsa if 4for"
print(f'\n>>> Tokenizando: "{text}"')
tokens = lexer(text)
print(tokens)
# assert [t.token_type for t in tokens] == [
#     "num",
#     "id",
#     "space",
#     "id",
#     "space",
#     "id",
#     "space",
#     "foreach",
#     "space",
#     "num",
#     "for",
#     "eof",
# ]
# assert [t.lex for t in tokens] == [
#     "4",
#     "forense",
#     " ",
#     "forforeach",
#     " ",
#     "for4foreach",
#     " ",
#     "foreach",
#     " ",
#     "4",
#     "for",
#     "$",
# ]
