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


# lexer = Lexer(
#     [
#         (
#             "string",
#             '"([^"])*"',
#         ),
#         ("id", "[a-zA-Z_][a-zA-Z_0-9]*"),
#         ("space", " *"),
#     ],
#     "eof",
# )
# input_texts = [
#     '"escaped" tanke "de guerra" quote "inside" print "outside"',
#     '"with multiple \\t\\n\\r escapes"',
#     '"with escape \\n sequence"',
#     '"simple"',
#     '"with space"',
#     '"with punctuation!"',
# ]

# for text in input_texts:
#     print(f'\n>>> Tokenizando: "{text}"')
#     tokens = lexer(text)
#     print(tokens)
#     # assert [t.token_type for t in tokens] == ["string", "eof"]
#     # assert [t.lex for t in tokens] == [text, "$"]
