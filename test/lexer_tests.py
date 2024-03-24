import unittest
from src.cmp.utils import Token
from src.lexical_analysis.lexer import Lexer


class TestLexer(unittest.TestCase):

    def test_identifier(self):
        lexer = Lexer(
            [
                ("id", "[a-zA-Z_][a-zA-Z0-9_]*"),
                ("space", " *"),
            ],
            "eof",
        )
        input_text = (
            "var1 _varName var_name2 FunctionName _1234 variableName123 _ _a _9"
        )

        expected_tokens = [
            Token("var1", "id"),
            Token(" ", "space"),
            Token("_varName", "id"),
            Token(" ", "space"),
            Token("var_name2", "id"),
            Token(" ", "space"),
            Token("FunctionName", "id"),
            Token(" ", "space"),
            Token("_1234", "id"),
            Token(" ", "space"),
            Token("variableName123", "id"),
            Token(" ", "space"),
            Token("_", "id"),
            Token(" ", "space"),
            Token("_a", "id"),
            Token(" ", "space"),
            Token("_9", "id"),
            Token("$", "eof"),
        ]

        result_tokens = lexer(input_text)
        self.assertEqual(
            len(result_tokens), len(expected_tokens), "Número incorrecto de tokens."
        )
        for result, expected in zip(result_tokens, expected_tokens):
            self.assertEqual(result.lex, expected.lex)
            self.assertEqual(result.token_type, expected.token_type)

    def test_number(self):
        lexer = Lexer(
            [
                ("num", "(\-|\+)?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][\+\-]?[0-9]+)?"),
                ("space", " *"),
            ],
            "eof",
        )
        input_text = "12345 +12345 -12345 123.45 +123.45 -123.45 1e10 1e+10 1e-10 +1e10 -1e10 +1e+10 +1e-10 -1e+10 -1e-10 1.23e10 1.23e+10 1.23e-10 +1.23e10 -1.23e10 +1.23e+10 +1.23e-10 -1.23e+10 -1.23e-10"
        expected_tokens = [
            Token("12345", "num"),
            Token(" ", "space"),
            Token("+12345", "num"),
            Token(" ", "space"),
            Token("-12345", "num"),
            Token(" ", "space"),
            Token("123.45", "num"),
            Token(" ", "space"),
            Token("+123.45", "num"),
            Token(" ", "space"),
            Token("-123.45", "num"),
            Token(" ", "space"),
            Token("1e10", "num"),
            Token(" ", "space"),
            Token("1e+10", "num"),
            Token(" ", "space"),
            Token("1e-10", "num"),
            Token(" ", "space"),
            Token("+1e10", "num"),
            Token(" ", "space"),
            Token("-1e10", "num"),
            Token(" ", "space"),
            Token("+1e+10", "num"),
            Token(" ", "space"),
            Token("+1e-10", "num"),
            Token(" ", "space"),
            Token("-1e+10", "num"),
            Token(" ", "space"),
            Token("-1e-10", "num"),
            Token(" ", "space"),
            Token("1.23e10", "num"),
            Token(" ", "space"),
            Token("1.23e+10", "num"),
            Token(" ", "space"),
            Token("1.23e-10", "num"),
            Token(" ", "space"),
            Token("+1.23e10", "num"),
            Token(" ", "space"),
            Token("-1.23e10", "num"),
            Token(" ", "space"),
            Token("+1.23e+10", "num"),
            Token(" ", "space"),
            Token("+1.23e-10", "num"),
            Token(" ", "space"),
            Token("-1.23e+10", "num"),
            Token(" ", "space"),
            Token("-1.23e-10", "num"),
            Token("$", "eof"),
        ]

        result_tokens = lexer(input_text)
        self.assertEqual(
            len(result_tokens), len(expected_tokens), "Número incorrecto de tokens."
        )
        for result, expected in zip(result_tokens, expected_tokens):
            self.assertEqual(result.lex, expected.lex)
            self.assertEqual(result.token_type, expected.token_type)

    def test_keywords(self):
        lexer = Lexer(
            [
                # Palabras clave
                ("print", "print"),
                ("if", "if"),
                ("else", "else"),
                ("let", "let"),
                ("in", "in"),
                ("for", "for"),
                ("function", "function"),
                ("type", "type"),
                ("space", " *"),
            ],
            "eof",
        )
        input_text = "print if else let in for function type"
        expected_tokens = [
            Token("print", "print"),
            Token(" ", "space"),
            Token("if", "if"),
            Token(" ", "space"),
            Token("else", "else"),
            Token(" ", "space"),
            Token("let", "let"),
            Token(" ", "space"),
            Token("in", "in"),
            Token(" ", "space"),
            Token("for", "for"),
            Token(" ", "space"),
            Token("function", "function"),
            Token(" ", "space"),
            Token("type", "type"),
            Token("$", "eof"),
        ]

        result_tokens = lexer(input_text)
        self.assertEqual(
            len(result_tokens), len(expected_tokens), "Número incorrecto de tokens."
        )
        for result, expected in zip(result_tokens, expected_tokens):
            self.assertEqual(result.lex, expected.lex)
            self.assertEqual(result.token_type, expected.token_type)

    def test_string_literals(self):
        lexer = Lexer(
            [
                (
                    "lit",
                    '"([^"]*)|([^\\"])*"',
                ),
            ],
            "eof",
        )
        input_texts = [
            '"simple"',
            '"with space"',
            '"with punctuation!"',
            '"with escape \\n sequence"',
            '"with multiple \\t\\n\\r escapes"',
            # '"escaped \\"quote\\" inside"',
        ]
        for input_text in input_texts:
            result_tokens = lexer(input_text)
            print(result_tokens)
            self.assertEqual(
                len(result_tokens), 2
            )  # Asegurándose de que solo haya un token mas el final
            self.assertEqual(
                result_tokens[0].lex, input_text
            )  # Verificar que el token coincida con el input
            self.assertEqual(
                result_tokens[0].token_type, "lit"
            )  # Verificar que el tipo de token sea 'string'

    def test_punctuation(self):
        lexer = Lexer(
            [
                ("dot", "\."),
                ("comma", ","),
                ("semicolon", ";"),
                ("colon", ":"),
                ("opar", "\("),
                ("cpar", "\)"),
                ("obracket", "\["),
                ("cbracket", "\]"),
                ("obrace", "\{"),
                ("cbrace", "\}"),
                ("plus", "\+"),
                ("minus", "\-"),
                ("star", "\*"),
                ("div", "\/"),
                ("exp", "\^"),
                ("assign", "="),
                ("lt", "<"),
                ("gt", ">"),
                ("excl", "!"),
                ("amp", "&"),
                ("pipe", "\|"),
                ("tilde", "~"),
                ("percent", "%"),
                ("space", " *"),
            ],
            "eof",
        )
        input_text = ". , ; : ( ) [ ] { } + - * / ^ = < > ! & | ~ %"
        expected_tokens = [
            Token(".", "dot"),
            Token(" ", "space"),
            Token(",", "comma"),
            Token(" ", "space"),
            Token(";", "semicolon"),
            Token(" ", "space"),
            Token(":", "colon"),
            Token(" ", "space"),
            Token("(", "opar"),
            Token(" ", "space"),
            Token(")", "cpar"),
            Token(" ", "space"),
            Token("[", "obracket"),
            Token(" ", "space"),
            Token("]", "cbracket"),
            Token(" ", "space"),
            Token("{", "obrace"),
            Token(" ", "space"),
            Token("}", "cbrace"),
            Token(" ", "space"),
            Token("+", "plus"),
            Token(" ", "space"),
            Token("-", "minus"),
            Token(" ", "space"),
            Token("*", "star"),
            Token(" ", "space"),
            Token("/", "div"),
            Token(" ", "space"),
            Token("^", "exp"),
            Token(" ", "space"),
            Token("=", "assign"),
            Token(" ", "space"),
            Token("<", "lt"),
            Token(" ", "space"),
            Token(">", "gt"),
            Token(" ", "space"),
            Token("!", "excl"),
            Token(" ", "space"),
            Token("&", "amp"),
            Token(" ", "space"),
            Token("|", "pipe"),
            Token(" ", "space"),
            Token("~", "tilde"),
            Token(" ", "space"),
            Token("%", "percent"),
            Token("$", "eof"),
        ]

        result_tokens = lexer(input_text)
        self.assertEqual(
            len(result_tokens), len(expected_tokens), "Número incorrecto de tokens."
        )
        for result, expected in zip(result_tokens, expected_tokens):
            self.assertEqual(result.lex, expected.lex)
            self.assertEqual(result.token_type, expected.token_type)

    def test_numerical_literals(self):
        # Test para literales numéricos y operaciones
        self.assertLexerOutput(
            "42;\n",
            expected_tokens=[
                Token("42", "num"),
                Token(";", "semicolon"),
                Token("\n", "newline"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            "print(42);",
            expected_tokens=[
                Token("print", "print"),
                Token("(", "opar"),
                Token("42", "num"),
                Token(")", "cpar"),
                Token(";", "semicolon"),
                Token("$", "eof"),
            ],
        )

    def test_string_literals_2(self):
        # Test para literales de cadena, incluyendo caracteres de escape
        self.assertLexerOutput(
            'print("Hello World");',
            expected_tokens=[
                Token("print", "print"),
                Token("(", "opar"),
                Token('"Hello World"', "lit"),
                Token(")", "cpar"),
                Token(";", "semicolon"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            'print("The message is \\"Hello World\\"");',
            expected_tokens=[
                Token("print", "print"),
                Token("(", "opar"),
                Token('"The message is \\"Hello World\\""', "lit"),
                Token(")", "cpar"),
                Token(";", "semicolon"),
                Token("$", "eof"),
            ],
        )

    def test_function_calls(self):
        # Test para llamadas a funciones y expresiones más complejas
        self.assertLexerOutput(
            "print(sin(2 * PI) ^ 2 + cos(3 * PI / log(4, 64)));",
            expected_tokens=[
                Token("print", "print"),
                Token("(", "opar"),
                Token("sin", "math_func"),
                Token("(", "opar"),
                Token("2", "num"),
                Token(" ", "space"),
                Token("*", "star"),
                Token(" ", "space"),
                Token("PI", "pi"),
                Token(")", "cpar"),
                Token(" ", "space"),
                Token("^", "exp"),
                Token(" ", "space"),
                Token("2", "num"),
                Token(" ", "space"),
                Token("+", "plus"),
                Token(" ", "space"),
                Token("cos", "math_func"),
                Token("(", "opar"),
                Token("3", "num"),
                Token(" ", "space"),
                Token("*", "star"),
                Token(" ", "space"),
                Token("PI", "pi"),
                Token(" ", "space"),
                Token("/", "div"),
                Token(" ", "space"),
                Token("log", "math_func"),
                Token("(", "opar"),
                Token("4", "num"),
                Token(",", "comma"),
                Token(" ", "space"),
                Token("64", "num"),
                Token(")", "cpar"),
                Token(")", "cpar"),
                Token(")", "cpar"),
                Token(";", "semicolon"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            "function tan(x) => sin(x) / cos(x);",
            expected_tokens=[
                Token("function", "function"),
                Token(" ", "space"),
                Token("tan", "math_func"),
                Token("(", "opar"),
                Token("x", "id"),
                Token(")", "cpar"),
                Token(" ", "space"),
                Token("=>", "arrow"),
                Token(" ", "space"),
                Token("sin", "math_func"),
                Token("(", "opar"),
                Token("x", "id"),
                Token(")", "cpar"),
                Token(" ", "space"),
                Token("/", "div"),
                Token(" ", "space"),
                Token("cos", "math_func"),
                Token("(", "opar"),
                Token("x", "id"),
                Token(")", "cpar"),
                Token(";", "semicolon"),
                Token("$", "eof"),
            ],
        )

    def test_control_structures(self):
        # Test para estructuras de control como if-else y bucles
        self.assertLexerOutput(
            'let a = 42 in if (a % 2 == 0) print("Even odd") else print("odd");',
            expected_tokens=[
                Token("let", "let"),
                Token(" ", "space"),
                Token("a", "id"),
                Token(" ", "space"),
                Token("=", "assign"),
                Token(" ", "space"),
                Token("42", "num"),
                Token(" ", "space"),
                Token("in", "in"),
                Token(" ", "space"),
                Token("if", "if"),
                Token(" ", "space"),
                Token("(", "opar"),
                Token("a", "id"),
                Token(" ", "space"),
                Token("%", "percent"),
                Token(" ", "space"),
                Token("2", "num"),
                Token(" ", "space"),
                Token("==", "eq"),
                Token(" ", "space"),
                Token("0", "num"),
                Token(")", "cpar"),
                Token(" ", "space"),
                Token("print", "print"),
                Token("(", "opar"),
                Token('"Even odd"', "lit"),
                Token(")", "cpar"),
                Token(" ", "space"),
                Token("else", "else"),
                Token(" ", "space"),
                Token("print", "print"),
                Token("(", "opar"),
                Token('"odd"', "lit"),
                Token(")", "cpar"),
                Token(";", "semicolon"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            "for (x in range(0, 10)) print(x);",
            expected_tokens=[
                Token("for", "for"),
                Token(" ", "space"),
                Token("(", "opar"),
                Token("x", "id"),
                Token(" ", "space"),
                Token("in", "in"),
                Token(" ", "space"),
                Token("range", "range"),
                Token("(", "opar"),
                Token("0", "num"),
                Token(",", "comma"),
                Token(" ", "space"),
                Token("10", "num"),
                Token(")", "cpar"),
                Token(")", "cpar"),
                Token(" ", "space"),
                Token("print", "print"),
                Token("(", "opar"),
                Token("x", "id"),
                Token(")", "cpar"),
                Token(";", "semicolon"),
                Token("$", "eof"),
            ],
        )

    def test_type_definitions(self):
        # Test para definiciones de tipos y uso de protocolos
        self.assertLexerOutput(
            "type Point { x = 0; y = 0; }",
            expected_tokens=[
                Token("type", "type"),
                Token(" ", "space"),
                Token("Point", "id"),
                Token(" ", "space"),
                Token("{", "obrace"),
                Token(" ", "space"),
                Token("x", "id"),
                Token(" ", "space"),
                Token("=", "assign"),
                Token(" ", "space"),
                Token("0", "num"),
                Token(";", "semicolon"),
                Token(" ", "space"),
                Token("y", "id"),
                Token(" ", "space"),
                Token("=", "assign"),
                Token(" ", "space"),
                Token("0", "num"),
                Token(";", "semicolon"),
                Token(" ", "space"),
                Token("}", "cbrace"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            "protocol Hashable { hash(): Number; }",
            expected_tokens=[
                Token("protocol", "protocol"),
                Token(" ", "space"),
                Token("Hashable", "id"),
                Token(" ", "space"),
                Token("{", "obrace"),
                Token(" ", "space"),
                Token("hash", "id"),
                Token("(", "opar"),
                Token(")", "cpar"),
                Token(":", "colon"),
                Token(" ", "space"),
                Token("Number", "id"),
                Token(";", "semicolon"),
                Token(" ", "space"),
                Token("}", "cbrace"),
                Token("$", "eof"),
            ],
        )

    def assertLexerOutput(self, input_text, expected_tokens: list[Token]):
        lexer = Lexer(
            [
                # numeros
                ("num", "(\-|\+)?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][\+\-]?[0-9]+)?"),
                # Espacios (para ser ignorados o manejados específicamente)
                ("space", " *"),
                # Nueva línea
                ("newline", "\n"),
                # Operadores de asignación y definición
                ("assign", "="),
                ("destructive_assign", ":="),
                ("colon", ":"),
                ("underscore", "_"),
                ("arrow", "=>"),
                # Operadores de comparación
                ("lt", "<"),
                ("le", "<="),
                ("gt", ">"),
                ("ge", ">="),
                ("eq", "=="),
                ("ne", "!="),
                # Palabras clave
                ("print", "print"),
                ("if", "if"),
                ("else", "else"),
                ("let", "let"),
                ("in", "in"),
                ("for", "for"),
                ("function", "function"),
                ("type", "type"),
                ("range", "range"),
                ("protocol", "protocol"),
                # Otros tokens especiales (como el operador de concatenación @)
                ("concat", "@"),
                # Funciones matemáticas y constantes
                ("math_func", "(sin|cos|tan|log|sqrt)"),
                ("pi", "PI"),
                # Identificadores
                ("id", "[a-zA-Z_][a-zA-Z0-9_]*"),
                # Cadenas de texto (incluyendo caracteres especiales)
                (
                    "lit",
                    '"([^"]|([^\\"]))*"',
                ),  #!no se como hacer que se detenga en en primer " que no sea \"
                # Signos de puntuacion
                ("dot", "\."),
                ("obracket", "\["),
                ("cbracket", "\]"),
                ("obrace", "\{"),
                ("cbrace", "\}"),
                ("plus", "\+"),
                ("minus", "\-"),
                ("star", "\*"),
                ("div", "\/"),
                ("exp", "\^"),
                ("assign", "="),
                ("lt", "<"),
                ("gt", ">"),
                ("excl", "!"),
                ("amp", "&"),
                ("pipe", "\|"),
                ("tilde", "~"),
                ("percent", "%"),
                ("opar", "\("),
                ("cpar", "\)"),
                ("semicolon", ";"),
                ("comma", ","),
            ],
            "eof",
        )

        result_tokens = lexer(input_text)
        for result, expected in zip(result_tokens, expected_tokens):
            self.assertEqual(result.lex, expected.lex)
            self.assertEqual(result.token_type, expected.token_type)


if __name__ == "__main__":
    unittest.main()
