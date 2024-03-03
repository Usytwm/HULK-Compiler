import string
from .tools.automaton import State
from .tools.automaton_builder import AutomatonBuilder


class Token:
    """
    Basic token class.

    Parameters
    ----------
    lex : str
        Token's lexeme.
    token_type : Enum
        Token's type.
    """

    def __init__(self, lex, token_type, value=None):
        self.lex = lex
        self.value = value
        if self.value is None:
            self.value = lex
        self.token_type = token_type

    def __str__(self):
        return f"{self.token_type}: {self.lex}"

    def __repr__(self):
        return str(self)

    @property
    def is_valid(self):
        return True


class Lexer:
    def __init__(self, eof):
        self.eof = eof
        self.automaton = self._build_automaton()

    def _build_automaton(self):
        automaton_builder = AutomatonBuilder()
        start = State("start")
        initial_states = []

        whitespace_automaton = automaton_builder.build_whitespace_automaton()
        identifier_automaton = automaton_builder.build_identifier_automaton()
        number_automaton = automaton_builder.build_number_automaton()
        punctuation_automaton = automaton_builder.build_punctuation_automaton()
        string_literal_automaton = automaton_builder.build_string_literal_automaton()
        operator_automaton = automaton_builder.build_operator_automaton()
        keyword_automaton = automaton_builder.build_keyword_automaton()
        initial_states.extend(
            [
                whitespace_automaton,
                identifier_automaton,
                number_automaton,
                punctuation_automaton,
                string_literal_automaton,
                operator_automaton,
                keyword_automaton,
            ]
        )

        for state in initial_states:
            start.add_epsilon_transition(state)
        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        lex = ""

        for symbol in string:
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

        return None, lex

    def _tokenize(self, text):
        while text:
            final, lex = self._walk(text)
            text = text[len(lex) :]
            if final:
                yield Token(lex, final.tag)

        yield Token("$", self.eof)

    def __call__(self, text):
        return [token for token in self._tokenize(text)]
