import unittest
from src.cmp.utils import Token
from src.lexical_analysis.lexer import Lexer


class TestLexer(unittest.TestCase):

    def test_identifier(self):
        lexer = Lexer(eof="eof")
        input_text = (
            "var1 _varName var_name2 FunctionName _1234 variableName123 _ _a _9"
        )

        expected_tokens = [
            Token("var1", "IDENTIFIER"),
            Token("_varName", "IDENTIFIER"),
            Token("var_name2", "IDENTIFIER"),
            Token("FunctionName", "IDENTIFIER"),
            Token("_1234", "IDENTIFIER"),
            Token("variableName123", "IDENTIFIER"),
            Token("_", "IDENTIFIER"),
            Token("_a", "IDENTIFIER"),
            Token("_9", "IDENTIFIER"),
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
        lexer = Lexer(eof="eof")
        input_text = "12345 +12345 -12345 123.45 +123.45 -123.45 1e10 1e+10 1e-10 +1e10 -1e10 +1e+10 +1e-10 -1e+10 -1e-10 1.23e10 1.23e+10 1.23e-10 +1.23e10 -1.23e10 +1.23e+10 +1.23e-10 -1.23e+10 -1.23e-10"
        expected_tokens = [
            Token("12345", "NUMBER"),
            Token("+12345", "NUMBER"),
            Token("-12345", "NUMBER"),
            Token("123.45", "NUMBER"),
            Token("+123.45", "NUMBER"),
            Token("-123.45", "NUMBER"),
            Token("1e10", "NUMBER"),
            Token("1e+10", "NUMBER"),
            Token("1e-10", "NUMBER"),
            Token("+1e10", "NUMBER"),
            Token("-1e10", "NUMBER"),
            Token("+1e+10", "NUMBER"),
            Token("+1e-10", "NUMBER"),
            Token("-1e+10", "NUMBER"),
            Token("-1e-10", "NUMBER"),
            Token("1.23e10", "NUMBER"),
            Token("1.23e+10", "NUMBER"),
            Token("1.23e-10", "NUMBER"),
            Token("+1.23e10", "NUMBER"),
            Token("-1.23e10", "NUMBER"),
            Token("+1.23e+10", "NUMBER"),
            Token("+1.23e-10", "NUMBER"),
            Token("-1.23e+10", "NUMBER"),
            Token("-1.23e-10", "NUMBER"),
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
        lexer = Lexer(eof="eof")

        for keyword, tag in " ".items():
            with self.subTest(keyword=keyword, tag=tag):
                input_text = keyword
                expected_tokens = [
                    Token(keyword, tag),
                    Token("$", "eof"),
                ]

                result_tokens = lexer(
                    input_text
                )  # Asegúrate de que esta sea la forma correcta de obtener tokens desde tu lexer.

                self.assertEqual(
                    len(result_tokens),
                    len(expected_tokens),
                    f"Número incorrecto de tokens para '{keyword}'.",
                )
                for result, expected in zip(result_tokens, expected_tokens):
                    self.assertEqual(
                        result.lex,
                        expected.lex,
                        f"Lexema incorrecto para '{keyword}'.",
                    )
                    self.assertEqual(
                        result.token_type,
                        expected.token_type,
                        f"Tipo de token incorrecto para '{keyword}'.",
                    )

    def test_string_literals(self):
        lexer = Lexer(eof="eof")
        # Lista de casos de prueba para literales de cadena
        string_cases = [
            ('"simple"', '"simple"'),
            ('"with space"', '"with space"'),
            ('"with punctuation!"', '"with punctuation!"'),
            ('"with escape \\n sequence"', '"with escape \\n sequence"'),
            ('"with multiple \\t\\n\\r escapes"', '"with multiple \\t\\n\\r escapes"'),
            ('"escaped \\"quote\\" inside"', '"escaped \\"quote\\" inside"'),
        ]

        for input_text, expected_content in string_cases:
            with self.subTest(input_text=input_text):
                expected_tokens = [
                    Token(expected_content, "LITERAL"),
                    Token("$", "eof"),
                ]

                result_tokens = lexer(input_text)

                self.assertEqual(
                    len(result_tokens),
                    len(expected_tokens),
                    f"Número incorrecto de tokens para literal de cadena '{input_text}'.",
                )
                for result, expected in zip(result_tokens, expected_tokens):
                    self.assertEqual(
                        result.lex,
                        expected.lex,
                        f"Lexema incorrecto para literal de cadena '{input_text}'.",
                    )
                    self.assertEqual(
                        result.token_type,
                        expected.token_type,
                        f"Tipo de token incorrecto para literal de cadena '{input_text}'.",
                    )

    def test_punctuation(self):
        lexer = Lexer(eof="eof")

        for sign in ".,;:()[]{}+-*/^=<>!&|~%".split():
            with self.subTest(sign=sign):
                input_text = sign
                expected_tokens = [
                    Token(sign, "PUNCTUATION"),
                    Token("$", "eof"),
                ]

                result_tokens = lexer(input_text)
                self.assertEqual(
                    len(result_tokens),
                    len(expected_tokens),
                    f"Número incorrecto de tokens para signo de puntuación '{sign}'.",
                )
                for result, expected in zip(result_tokens, expected_tokens):
                    self.assertEqual(
                        result.lex,
                        expected.lex,
                        f"Lexema incorrecto para signo de puntuación '{sign}'.",
                    )
                    self.assertEqual(
                        result.token_type,
                        expected.token_type,
                        f"Tipo de token incorrecto para signo de puntuación '{sign}'.",
                    )

    def test_numerical_literals(self):
        # Test para literales numéricos y operaciones
        self.assertLexerOutput(
            "42;",
            expected_tokens=[
                Token("42", "NUMBER"),
                Token(";", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            "print(42);",
            expected_tokens=[
                Token("print", "print"),
                Token("(", "PUNCTUATION"),
                Token("42", "NUMBER"),
                Token(")", "PUNCTUATION"),
                Token(";", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )

    def test_string_literals_2(self):
        # Test para literales de cadena, incluyendo caracteres de escape
        self.assertLexerOutput(
            'print("Hello World");',
            expected_tokens=[
                Token("print", "print"),
                Token("(", "PUNCTUATION"),
                Token('"Hello World"', "LITERAL"),
                Token(")", "PUNCTUATION"),
                Token(";", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            'print("The message is \\"Hello World\\"");',
            expected_tokens=[
                Token("print", "print"),
                Token("(", "PUNCTUATION"),
                Token('"The message is \\"Hello World\\""', "LITERAL"),
                Token(")", "PUNCTUATION"),
                Token(";", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )

    def test_function_calls(self):
        # Test para llamadas a funciones y expresiones más complejas
        self.assertLexerOutput(
            "print(sin(2 * PI) ^ 2 + cos(3 * PI / log(4, 64)));",
            expected_tokens=[
                Token("print", "print"),
                Token("(", "PUNCTUATION"),
                Token("sin", "sin"),
                Token("(", "PUNCTUATION"),
                Token("2", "NUMBER"),
                Token("*", "OPERATOR"),
                Token("PI", "constant"),
                Token(")", "PUNCTUATION"),
                Token("^", "OPERATOR"),
                Token("2", "NUMBER"),
                Token("+", "OPERATOR"),
                Token("cos", "cos"),
                Token("(", "PUNCTUATION"),
                Token("3", "NUMBER"),
                Token("*", "OPERATOR"),
                Token("PI", "constant"),
                Token("/", "OPERATOR"),
                Token("log", "log"),
                Token("(", "PUNCTUATION"),
                Token("4", "NUMBER"),
                Token(",", "PUNCTUATION"),
                Token("64", "NUMBER"),
                Token(")", "PUNCTUATION"),
                Token(")", "PUNCTUATION"),
                Token(")", "PUNCTUATION"),
                Token(";", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            "function tan(x) => sin(x) / cos(x);",
            expected_tokens=[
                Token("function", "function"),
                Token("tan", "IDENTIFIER"),
                Token("(", "PUNCTUATION"),
                Token("x", "IDENTIFIER"),
                Token(")", "PUNCTUATION"),
                Token("=>", "OPERATOR"),
                Token("sin", "sin"),
                Token("(", "PUNCTUATION"),
                Token("x", "IDENTIFIER"),
                Token(")", "PUNCTUATION"),
                Token("/", "OPERATOR"),
                Token("cos", "cos"),
                Token("(", "PUNCTUATION"),
                Token("x", "IDENTIFIER"),
                Token(")", "PUNCTUATION"),
                Token(";", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )

    def test_control_structures(self):
        # Test para estructuras de control como if-else y bucles
        self.assertLexerOutput(
            'let a = 42 in if (a % 2 == 0) print("Even") else print("odd");',
            expected_tokens=[
                Token("let", "let"),
                Token("a", "IDENTIFIER"),
                Token("=", "OPERATOR"),
                Token("42", "NUMBER"),
                Token("in", "in"),
                Token("if", "if"),
                Token("(", "PUNCTUATION"),
                Token("a", "IDENTIFIER"),
                Token("%", "OPERATOR"),
                Token("2", "NUMBER"),
                Token("==", "OPERATOR"),
                Token("0", "NUMBER"),
                Token(")", "PUNCTUATION"),
                Token("print", "print"),
                Token("(", "PUNCTUATION"),
                Token('"Even"', "LITERAL"),
                Token(")", "PUNCTUATION"),
                Token("else", "else"),
                Token("print", "print"),
                Token("(", "PUNCTUATION"),
                Token('"odd"', "LITERAL"),
                Token(")", "PUNCTUATION"),
                Token(";", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            "for (x in range(0, 10)) print(x);",
            expected_tokens=[
                Token("for", "for"),
                Token("(", "PUNCTUATION"),
                Token("x", "IDENTIFIER"),
                Token("in", "in"),
                Token("range", "range"),
                Token("(", "PUNCTUATION"),
                Token("0", "NUMBER"),
                Token(",", "PUNCTUATION"),
                Token("10", "NUMBER"),
                Token(")", "PUNCTUATION"),
                Token(")", "PUNCTUATION"),
                Token("print", "print"),
                Token("(", "PUNCTUATION"),
                Token("x", "IDENTIFIER"),
                Token(")", "PUNCTUATION"),
                Token(";", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )

    def test_type_definitions(self):
        # Test para definiciones de tipos y uso de protocolos
        self.assertLexerOutput(
            "type Point { x = 0; y = 0; }",
            expected_tokens=[
                Token("type", "type"),
                Token("Point", "IDENTIFIER"),
                Token("{", "PUNCTUATION"),
                Token("x", "IDENTIFIER"),
                Token("=", "OPERATOR"),
                Token("0", "NUMBER"),
                Token(";", "PUNCTUATION"),
                Token("y", "IDENTIFIER"),
                Token("=", "OPERATOR"),
                Token("0", "NUMBER"),
                Token(";", "PUNCTUATION"),
                Token("}", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            "protocol Hashable { hash(): Number; }",
            expected_tokens=[
                Token("protocol", "protocol"),
                Token("Hashable", "IDENTIFIER"),
                Token("{", "PUNCTUATION"),
                Token("hash", "IDENTIFIER"),
                Token("(", "PUNCTUATION"),
                Token(")", "PUNCTUATION"),
                Token(":", "OPERATOR"),
                Token("Number", "IDENTIFIER"),
                Token(";", "PUNCTUATION"),
                Token("}", "PUNCTUATION"),
                Token("$", "eof"),
            ],
        )

    def assertLexerOutput(self, input_text, expected_tokens: list[Token]):
        lexer = Lexer(eof="eof")
        result_tokens = lexer(input_text)
        for result, expected in zip(result_tokens, expected_tokens):
            self.assertEqual(result.lex, expected.lex)
            self.assertEqual(result.token_type, expected.token_type)


if __name__ == "__main__":
    unittest.main()
