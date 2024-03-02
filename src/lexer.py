import string
from tools.automata import State


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

    def __init__(self, lex, token_type):
        self.lex = lex
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
        start = State("start")
        initial_states = []

        #! ESPACIOS EN BLANCO
        ws_state = State("whitespace")
        for ws_char in " \t\n":
            ws_state.add_transition(ws_char, ws_state)

        # Añade una transición desde el estado inicial hacia el estado de espacios en blanco
        start.add_epsilon_transition(ws_state)

        #! IDENTIFICADORES
        id_state = State("id")
        initial_states.append(id_state)
        id_state_final = State("id_final", True)
        id_state_final.tag = "IDENTIFIER"
        for i in string.ascii_letters + "_":
            id_state.add_transition(i, id_state_final)
        for i in string.ascii_letters + string.digits + "_":
            id_state_final.add_transition(i, id_state_final)

        #! NUMEROS
        num_state = State("num")
        initial_states.append(num_state)
        num_state_final = State("num_final", True)
        num_state_final.tag = "NUMBER"
        for i in string.digits:
            num_state.add_transition(i, num_state_final)
            num_state_final.add_transition(i, num_state_final)

        # #! NUMEROS
        # num_state = State("num")
        # initial_states.append(num_state)
        # num_integer_part = State("num_integer_part")
        # num_decimal_part = State("num_decimal_part")
        # num_exponent_part = State("num_exponent_part")
        # num_state_final = State("num_final", True)
        # num_state_final.tag = "NUMBER"

        # # Transiciones para la parte entera del número
        # for digit in string.digits:
        #     num_state.add_transition(digit, num_integer_part)
        #     num_integer_part.add_transition(digit, num_integer_part)

        # # Transición para el punto decimal
        # num_integer_part.add_transition('.', num_decimal_part)

        # # Transiciones para la parte decimal después del punto
        # for digit in string.digits:
        #     num_decimal_part.add_transition(digit, num_decimal_part)

        # # Transición para iniciar la parte del exponente (e o E)
        # num_decimal_part.add_transition('e', num_exponent_part)
        # num_decimal_part.add_transition('E', num_exponent_part)
        # num_integer_part.add_transition('e', num_exponent_part)
        # num_integer_part.add_transition('E', num_exponent_part)

        # # Transiciones para la parte del exponente después de 'e' o 'E'
        # for digit in string.digits:
        #     num_exponent_part.add_transition(digit, num_exponent_part)

        # # Opcional: manejar signos '+' o '-' después de 'e' o 'E'
        # num_exponent_sign = State("num_exponent_sign")
        # num_exponent_part.add_transition('+', num_exponent_sign)
        # num_exponent_part.add_transition('-', num_exponent_sign)
        # for digit in string.digits:
        #     num_exponent_sign.add_transition(digit, num_exponent_part)

        # # Asegurarse de que la parte final del número sea reconocida como final
        # num_integer_part.add_transition('e', num_exponent_part, is_final=True)
        # num_integer_part.add_transition('E', num_exponent_part, is_final=True)
        # num_decimal_part.add_transition('e', num_exponent_part, is_final=True)
        # num_decimal_part.add_transition('E', num_exponent_part, is_final=True)
        # num_exponent_part.is_final = True

        #! PUNTUACION
        punc_state = State("punc")
        initial_states.append(punc_state)
        punc_state_final = State("punc_final", True)
        punc_state_final.tag = "PUNCTUATION"
        punctuation_signs = ";,().{}[]"
        for sign in punctuation_signs:
            punc_state.add_transition(sign, punc_state_final)

        #! LITERALES DE CADENA
        lit_start_state = State("lit_start")
        initial_states.append(lit_start_state)
        lit_content_state = State("lit_content")
        lit_escape_state = State(
            "lit_escape"
        )  # Estado para manejar el carácter de escape
        lit_end_state = State(
            "lit_end", True
        )  # Estado final para cuando se cierra la cadena
        lit_end_state.tag = "LITERAL"
        # Transición desde el estado inicial para comenzar una cadena literal
        lit_start_state.add_transition('"', lit_content_state)

        # Transiciones para manejar el contenido de la cadena
        # Esto permite cualquier caracter excepto la comilla doble que termina la cadena
        for char in (
            string.ascii_letters
            + string.digits
            + string.punctuation.replace('"', "")
            + " "
        ):
            lit_content_state.add_transition(char, lit_content_state)
        lit_content_state.add_transition("\\", lit_escape_state)
        lit_escape_state.add_transition('"', lit_content_state)
        for char in ("\\", '"', "n", "t", "r"):
            lit_escape_state.add_transition(char, lit_content_state)

        # Transición para cerrar la cadena y moverse al estado final
        lit_content_state.add_transition('"', lit_end_state)

        #! OPERADORES
        op_state = State("op")
        initial_states.append(op_state)
        # Estados finales para operadores de un solo carácter
        op_single_final_states = {op: State(f"op_{op}_final", True) for op in "+-*/^%"}

        # Añade transiciones para operadores de un solo carácter
        for op, state in op_single_final_states.items():
            state.tag = "OPERATOR"
            op_state.add_transition(op, state)

        # Operadores de dos caracteres y sus estados intermedios
        op_double_chars = {
            "=": ["=", ">"],
            "!": ["="],
            ">": ["="],
            "<": ["="],
            "&": ["&"],
            "|": ["|"],
            "*": ["*"],
            "@": ["@"],
            ":": ["="],
        }
        op_double_final_states = {}
        op_double_intermediate_states = {}

        for op, next_chars in op_double_chars.items():
            for next_char in next_chars:
                # Estado intermedio para el primer carácter
                if op not in op_double_intermediate_states:
                    op_double_intermediate_states[op] = State(
                        f"op_{op}_intermediate", True
                    )
                    op_double_intermediate_states[op].tag = "OPERATOR"

                # Estado final para la combinación de dos caracteres
                final_state = State(f"op_{op}{next_char}_final", True)
                final_state.tag = "OPERATOR"
                op_double_final_states[f"{op}{next_char}"] = final_state

                # Añade transición desde el estado inicial al estado intermedio
                op_state.add_transition(op, op_double_intermediate_states[op])

                # Añade transición desde el estado intermedio al estado final
                op_double_intermediate_states[op].add_transition(next_char, final_state)

        #! PALABRAS CLAVES
        # Diccionario de palabras clave
        keywords = {
            "true": "true",
            "false": "false",
            "PI": "constant",
            "E": "constant",
            "print": "print",
            "sqrt": "sqrt",
            "cos": "cos",
            "exp": "exp",
            "log": "log",
            "rand": "rand",
            "function": "function",
            "let": "let",
            "in": "in",
            "if": "if",
            "else": "else",
            "while": "while",
            "for": "for",
            "range": "range",
            "type": "type",
            "self": "self",
            "new": "new",
            "inherits": "inherits",
            "protocol": "protocol",
            "extends": "extends",
        }

        keyword_start = State("keyword_start")
        initial_states.append(keyword_start)
        # Añadir estados y transiciones para cada palabra clave
        for keyword, tag in keywords.items():
            current_state = keyword_start
            for char in keyword[:-1]:  # Iterar hasta el penúltimo caracter
                # Crear un nuevo estado intermedio si es necesario
                next_state = current_state.transitions.get(char)
                if next_state is None:
                    next_state = State(f"{char}")
                    current_state.add_transition(char, next_state)
                else:
                    next_state = next_state[0]
                current_state = next_state

            # Añadir el último caracter de la palabra clave
            # El estado final lleva el tag de la palabra clave
            final_state = State(f"{keyword}_final", True)
            final_state.tag = tag
            current_state.add_transition(keyword[-1], final_state)

            # Retorna el estado inicial del NFA

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


lexer = Lexer(
    "eof",
)

with open("test/Data/prueba.txt", "r", encoding="utf-8") as archivo:
    texto = archivo.read()

lexer = Lexer("eof")
for token in lexer._tokenize(texto):
    print(token)
