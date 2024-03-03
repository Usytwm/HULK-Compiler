# config.py
import string

# Palabras clave
keywords = {
    "true": "true",
    "false": "false",
    "PI": "constant",
    "E": "constant",
    "print": "print",
    "sqrt": "sqrt",
    "cos": "cos",
    "sin": "sin",
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

# Signos de puntuación
punctuation_signs = ";,().{}[]"

# Operadores de un solo carácter
single_operators = "+-*/^%"

# Operadores de dos caracteres y sus combinaciones válidas
double_operators = {
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


digits = string.digits

letters = string.ascii_letters

ascii_letters_and_digits = letters + digits

ascii_letters_and_digits_and_underscore = ascii_letters_and_digits + "_"

ascii_letters_and_underscore = letters + "_"
