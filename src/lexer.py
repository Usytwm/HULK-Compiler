from .tools.automaton import State
from .tools.automaton_builder import AutomatonBuilder


class Token:
    """
    Representa un token en el contexto de análisis léxico.

    Un token es una secuencia de caracteres que tienen un significado colectivo
    en el contexto del lenguaje que se está analizando.

    Parameters
    ----------
    lex : str
        El lexema o secuencia de caracteres que forma el token.
    token_type : Enum
        El tipo de token, determinado por su función gramatical o sintáctica.
    value : Any, optional
        El valor asociado al token, si es distinto de su representación textual.
        Por defecto es None, indicando que no hay un valor distinto al lexema.
    row : int, optional
        La fila en el texto fuente donde se encuentra el token. Por defecto es None.
    column : int, optional
        La columna en el texto fuente donde comienza el token. Por defecto es None.

    Attributes
    ----------
    lex : str
        Lexema del token.
    value : Any
        Valor asociado al token.
    token_type : Enum
        Tipo de token.
    row : int
        Fila en el texto fuente.
    column : int
        Columna en el texto fuente.

    Methods
    -------
    __str__()
        Devuelve una representación en cadena del token.
    __repr__()
        Devuelve una representación más formal del token.
    is_valid
        Propiedad que verifica si el token es válido.
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
        """
        Devuelve una representación en cadena de la instancia de Token.

        Returns
        -------
        str
            Una cadena que representa el token, incluyendo su tipo, lexema,
            valor (si aplica), y su posición (fila y columna) en el texto fuente.
        """
        return f"Tokentype:{self.token_type}\nLexeme:{self.lex}\nValue:{self.value}\nrow:{self.row} , column:{self.column}"

    def __repr__(self):
        """
        Devuelve una representación formal de la instancia de Token.

        Esta representación es útil para depuración y registro en logs.

        Returns
        -------
        str
            Una representación en cadena que puede ser utilizada para recrear
            la instancia del token.
        """
        return str(self)

    @property
    def is_valid(self):
        """
        Verifica si el token es válido.

        Este método podría ser extendido para implementar lógica específica
        de validación.

        Returns
        -------
        bool
            Siempre devuelve True. Debe ser sobreescrito para cambiar
            la lógica de validación.
        """
        return True


class Lexer:
    """
    Analizador léxico para identificar tokens en un texto fuente.

    Utiliza autómatas finitos para reconocer patrones que definen los distintos
    tipos de tokens del lenguaje que se está analizando.

    Parameters
    ----------
    eof : Any
        Representación del token de fin de archivo utilizado para marcar el final
        del texto fuente.

    Attributes
    ----------
    eof : Any
        Token de fin de archivo.
    automaton : State
        Estado inicial del autómata finito determinista construido para el análisis.

    Methods
    -------
    _build_automaton()
        Construye el autómata finito determinista utilizado para el análisis léxico.
    _walk(string)
        Avanza a través del texto fuente, identificando el próximo token.
    _tokenize(text)
        Procesa el texto fuente completo, generando tokens.
    __call__(text)
        Permite que la instancia de Lexer se comporte como una función, analizando
        el texto fuente y devolviendo los tokens identificados.
    """

    def __init__(self, eof):
        self.eof = eof
        self.automaton = self._build_automaton()

    def _build_automaton(self):
        """
        Construye y devuelve el autómata finito determinista utilizado para el análisis léxico.

        Este método combina varios autómatas menores que reconocen los distintos patrones
        de tokens (como identificadores, literales numéricos, etc.) en un único autómata.

        Returns
        -------
        State
            El estado inicial del autómata finito determinista construido.
        """
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
        """
        Avanza a través de la cadena de entrada, identificando el próximo token.

        Parameters
        ----------
        string : str
            La cadena de entrada desde la cual se están extrayendo tokens.

        Returns
        -------
        tuple
            Un par (final, lex), donde 'final' es el estado final alcanzado en
            el autómata (si alguno) y 'lex' es el lexema del token identificado.
            Si no se identifica un token, 'final' será None.
        """
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
        """
        Procesa el texto fuente completo, generando tokens.

        Este método es un generador que produce tokens a medida que analiza
        el texto fuente.

        Parameters
        ----------
        text : str
            El texto fuente que será analizado para extracción de tokens.

        Yields
        ------
        Token
            Los tokens identificados en el texto fuente.
        """
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
        """
        Permite que la instancia de Lexer se comporte como una función.

        Analiza el texto fuente y devuelve una lista de tokens identificados.

        Parameters
        ----------
        text : str
            El texto fuente que será analizado para extracción de tokens.

        Returns
        -------
        list of Token
            Una lista de los tokens identificados en el texto fuente.
        """
        return [token for token in self._tokenize(text)]
