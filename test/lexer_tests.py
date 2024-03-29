import unittest
from src.cmp.utils import Token
from src.lexical_analysis.lexer import Lexer
from src.lexical_analysis.regex_patterns import build_regex


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
            Token("_varName", "id"),
            Token("var_name2", "id"),
            Token("FunctionName", "id"),
            Token("_1234", "id"),
            Token("variableName123", "id"),
            Token("_", "id"),
            Token("_a", "id"),
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
            Token("+12345", "num"),
            Token("-12345", "num"),
            Token("123.45", "num"),
            Token("+123.45", "num"),
            Token("-123.45", "num"),
            Token("1e10", "num"),
            Token("1e+10", "num"),
            Token("1e-10", "num"),
            Token("+1e10", "num"),
            Token("-1e10", "num"),
            Token("+1e+10", "num"),
            Token("+1e-10", "num"),
            Token("-1e+10", "num"),
            Token("-1e-10", "num"),
            Token("1.23e10", "num"),
            Token("1.23e+10", "num"),
            Token("1.23e-10", "num"),
            Token("+1.23e10", "num"),
            Token("-1.23e10", "num"),
            Token("+1.23e+10", "num"),
            Token("+1.23e-10", "num"),
            Token("-1.23e+10", "num"),
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
            Token("if", "if"),
            Token("else", "else"),
            Token("let", "let"),
            Token("in", "in"),
            Token("for", "for"),
            Token("function", "function"),
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
                    '"([^"])*"',
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
            '"escaped \\"quote\\" inside"',
        ]
        for input_text in input_texts:
            result_tokens = lexer(input_text)
            self.assertEqual(
                len(result_tokens), 2
            )  # Asegurándose de que solo haya un token mas el final
            self.assertEqual(
                result_tokens[0].lex, input_text
            )  # Verificar que el token coincida con el input
            self.assertEqual(
                result_tokens[0].token_type, "lit"
            )  # Verificar que el tipo de token sea 'lit'

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
            Token(",", "comma"),
            Token(";", "semicolon"),
            Token(":", "colon"),
            Token("(", "opar"),
            Token(")", "cpar"),
            Token("[", "obracket"),
            Token("]", "cbracket"),
            Token("{", "obrace"),
            Token("}", "cbrace"),
            Token("+", "plus"),
            Token("-", "minus"),
            Token("*", "star"),
            Token("/", "div"),
            Token("^", "exp"),
            Token("=", "assign"),
            Token("<", "lt"),
            Token(">", "gt"),
            Token("!", "excl"),
            Token("&", "amp"),
            Token("|", "pipe"),
            Token("~", "tilde"),
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
            'print("The message is \\"Hello World\\" \\n \\t \\r");',
            expected_tokens=[
                Token("print", "print"),
                Token("(", "opar"),
                Token('"The message is \\"Hello World\\" \\n \\t \\r"', "lit"),
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
                Token("*", "star"),
                Token("PI", "pi"),
                Token(")", "cpar"),
                Token("^", "exp"),
                Token("2", "num"),
                Token("+", "plus"),
                Token("cos", "math_func"),
                Token("(", "opar"),
                Token("3", "num"),
                Token("*", "star"),
                Token("PI", "pi"),
                Token("/", "div"),
                Token("log", "math_func"),
                Token("(", "opar"),
                Token("4", "num"),
                Token(",", "comma"),
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
                Token("tan", "math_func"),
                Token("(", "opar"),
                Token("x", "id"),
                Token(")", "cpar"),
                Token("=>", "arrow"),
                Token("sin", "math_func"),
                Token("(", "opar"),
                Token("x", "id"),
                Token(")", "cpar"),
                Token("/", "div"),
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
                Token("a", "id"),
                Token("=", "assign"),
                Token("42", "num"),
                Token("in", "in"),
                Token("if", "if"),
                Token("(", "opar"),
                Token("a", "id"),
                Token("%", "percent"),
                Token("2", "num"),
                Token("==", "eq"),
                Token("0", "num"),
                Token(")", "cpar"),
                Token("print", "print"),
                Token("(", "opar"),
                Token('"Even odd"', "lit"),
                Token(")", "cpar"),
                Token("else", "else"),
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
                Token("(", "opar"),
                Token("x", "id"),
                Token("in", "in"),
                Token("range", "range"),
                Token("(", "opar"),
                Token("0", "num"),
                Token(",", "comma"),
                Token("10", "num"),
                Token(")", "cpar"),
                Token(")", "cpar"),
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
                Token("Point", "id"),
                Token("{", "obrace"),
                Token("x", "id"),
                Token("=", "assign"),
                Token("0", "num"),
                Token(";", "semicolon"),
                Token("y", "id"),
                Token("=", "assign"),
                Token("0", "num"),
                Token(";", "semicolon"),
                Token("}", "cbrace"),
                Token("$", "eof"),
            ],
        )
        self.assertLexerOutput(
            "protocol Hashable { hash(): Number; }",
            expected_tokens=[
                Token("protocol", "protocol"),
                Token("Hashable", "id"),
                Token("{", "obrace"),
                Token("hash", "id"),
                Token("(", "opar"),
                Token(")", "cpar"),
                Token(":", "colon"),
                Token("Number", "id"),
                Token(";", "semicolon"),
                Token("}", "cbrace"),
                Token("$", "eof"),
            ],
        )

    def test_external_code(self):
        path = "test/Data/prueba.txt"
        with open(path, "r", encoding="utf-8") as archivo:
            content = archivo.read()
            lexer = Lexer(
                build_regex(),
                "eof",
            )
            result_tokens = lexer(content)
            print(result_tokens)


        
    def assertLexerOutput(self, input_text, expected_tokens: list[Token]):
        lexer = Lexer(
            build_regex(),
            "eof",
        )
        

        result_tokens = lexer(input_text)
        print("Resultado")
        print(result_tokens)
        # Iterar sobre los tokens resultantes y los esperados
        for i, (result, expected) in enumerate(zip(result_tokens, expected_tokens)):
            # Utilizar assertEqual para comparar los lexemas y tipos de tokens, con un mensaje de error personalizado
            self.assertEqual(
                result.lex,
                expected.lex,
                f"Error en el lexema numero {i}, token -> {expected}: Esperado: '{expected.lex}', Obtenido: '{result.lex}'",
            )
            self.assertEqual(
                result.token_type,
                expected.token_type,
                f"Error en el tipo del token numero {i}, token -> {expected}: Esperado: '{expected.token_type}', Obtenido: '{result.token_type}'",
            )


if __name__ == "__main__":
    unittest.main()
