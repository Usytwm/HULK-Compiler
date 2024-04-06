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
    def __init__(self, table, eof, includesapces=True):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()
        self.spaces = includesapces

    def _build_regexs(self, table):
        """toma una tabla de tipos de tokens y sus correspondientes expresiones regulares,
        y construye un autómata para cada uno. Cada estado final en el autómata se etiqueta
        con su índice y tipo de token correspondiente."""
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
        """onstruye un autómata determinístico a partir de los autómatas en regexs.
        Cada autómata se conecta al estado inicial a través de una transición epsilon.
        """
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

            if self.spaces and final[0][1] == "space":
                continue
            if final[0][1] == "comment":
                continue
            yield lex, final[0][1]

        yield "$", self.eof

    def __call__(self, text):
        return [Token(lex, ttype) for lex, ttype in self._tokenize(text)]
