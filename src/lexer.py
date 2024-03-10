from tools.automaton import State
from tools.automaton_builder import AutomatonBuilder


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

    def __init__(self, lex, token_type, value=None, row=None, column=None):
        self.lex = lex
        self.value = value
        if self.value is None:
            self.value = lex
        self.token_type = token_type
        self.row = row
        self.column = column

    def __str__(self):
        return f"Tokentype:{self.token_type}\nLexeme:{self.lex}\nValue:{self.value}\nrow:{self.row} , column:{self.column}"

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
        row, column = 1, 1

        while text:
            final, lex = self._walk(text)
            new_lines = lex.count("\n")
            if new_lines > 0:
                row += new_lines
                column = len(lex) - lex.rfind("\n")
            else:
                column += len(lex)
            text = text[len(lex) :]
            if final:
                try:
                    value = float(lex) if "." in lex else int(lex)
                    yield Token(
                        lex, final.tag, value=value, row=row, column=column - len(lex)
                    )
                except ValueError:
                    yield Token(lex, final.tag, row=row, column=column - len(lex))
            elif lex == "":
                raise ValueError

        yield Token("$", self.eof)

    def __call__(self, text):
        return [token for token in self._tokenize(text)]
