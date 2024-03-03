# automaton_builder.py
from .automaton import State
import string
from .config import (
    keywords,
    double_operators,
    single_operators,
    punctuation_signs,
    ascii_letters_and_digits_and_underscore,
    ascii_letters_and_underscore,
    ascii_letters_and_digits,
    digits,
)


class AutomatonBuilder:

    @staticmethod
    def build_whitespace_automaton():
        ws_state = State("whitespace")
        for ws_char in " \t\n":
            ws_state.add_transition(ws_char, ws_state)
        return ws_state

    @staticmethod
    def build_identifier_automaton():
        id_state = State("id")
        id_state_final = State("id_final", True)
        id_state_final.tag = "IDENTIFIER"
        for i in ascii_letters_and_underscore:
            id_state.add_transition(i, id_state_final)
        for i in ascii_letters_and_digits_and_underscore:
            id_state_final.add_transition(i, id_state_final)
        return id_state

    @staticmethod
    def build_number_automaton():
        num_state = State("num")
        num_integer_part = State("num_integer_part", True)
        num_integer_part.tag = "NUMBER"
        num_decimal_part = State("num_decimal_part")
        num_decimal_part_final = State("num_decimal_part_final", True)
        num_decimal_part_final.tag = "NUMBER"
        num_exponent_part = State("num_exponent_part")
        num_exponent_sign = State("num_exponent_sign")
        num_state_final = State("num_final", True)
        num_state_final.tag = "NUMBER"
        sign_state = State("sign")

        # Transiciones desde el estado inicial para manejar los signos
        num_state.add_transition("-", sign_state)
        num_state.add_transition("+", sign_state)
        for i in digits:
            sign_state.add_transition(i, num_integer_part)
            num_state.add_transition(i, num_integer_part)
            num_integer_part.add_transition(i, num_integer_part)

        num_integer_part.add_transition("e", num_exponent_part)
        num_integer_part.add_transition("E", num_exponent_part)
        num_integer_part.add_transition("e", num_exponent_part)
        num_integer_part.add_transition("E", num_exponent_part)

        # Transición para el punto decimal
        num_integer_part.add_transition(".", num_decimal_part)

        # Transiciones para la parte decimal después del punto
        for digit in digits:
            num_decimal_part.add_transition(digit, num_decimal_part_final)
            num_decimal_part_final.add_transition(digit, num_decimal_part_final)

        # Transición para iniciar la parte del exponente (e o E)
        num_decimal_part_final.add_transition("e", num_exponent_part)
        num_decimal_part_final.add_transition("E", num_exponent_part)
        num_decimal_part_final.add_transition("e", num_exponent_part)
        num_decimal_part_final.add_transition("E", num_exponent_part)

        # Manejar signos '+' o '-' después de 'e' o 'E'
        num_exponent_part.add_transition("+", num_exponent_sign)
        num_exponent_part.add_transition("-", num_exponent_sign)
        for digit in digits:
            num_exponent_sign.add_transition(digit, num_exponent_part)
            num_exponent_part.add_transition(digit, num_state_final)
            num_state_final.add_transition(digit, num_state_final)

        return num_state

    @staticmethod
    def build_punctuation_automaton(punctuation_signs=punctuation_signs):
        punc_state = State("punc")
        punc_state_final = State("punc_final", True)
        punc_state_final.tag = "PUNCTUATION"
        for sign in punctuation_signs:
            punc_state.add_transition(sign, punc_state_final)
        return punc_state

    @staticmethod
    def build_string_literal_automaton():
        lit_start_state = State("lit_start")
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
            ascii_letters_and_digits + string.punctuation.replace('"', "") + " "
        ):
            lit_content_state.add_transition(char, lit_content_state)
        lit_content_state.add_transition("\\", lit_escape_state)
        lit_escape_state.add_transition('"', lit_content_state)
        for char in ("\\", '"', "n", "t", "r"):
            lit_escape_state.add_transition(char, lit_content_state)

        # Transición para cerrar la cadena y moverse al estado final
        lit_content_state.add_transition('"', lit_end_state)

        return lit_start_state

    @staticmethod
    def build_operator_automaton():
        op_state = State("op")
        # Estados finales para operadores de un solo carácter
        op_single_final_states = {
            op: State(f"op_{op}_final", True) for op in single_operators
        }

        # Añade transiciones para operadores de un solo carácter
        for op, state in op_single_final_states.items():
            state.tag = "OPERATOR"
            op_state.add_transition(op, state)

        op_double_final_states = {}
        op_double_intermediate_states = {}

        for op, next_chars in double_operators.items():
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

        return op_state

    @staticmethod
    def build_keyword_automaton(keywords: dict[str, str] = keywords):
        keyword_start = State("keyword_start")
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

        return keyword_start
