import os
import sys
import unittest
from src.lexer import Lexer, Token

# sys.path.insert(0, os.getcwd() + "test/lexer_tests")


class TestLexer(unittest.TestCase):
    def test_identifier(self):
        lexer = Lexer(eof="eof")
        input_text = "variableName"
        expected_tokens = [Token("variableName", "IDENTIFIER"), Token("$", "eof")]

        result_tokens = lexer(input_text)
        self.assertEqual(
            len(result_tokens), len(expected_tokens), "Número incorrecto de tokens."
        )
        for result, expected in zip(result_tokens, expected_tokens):
            self.assertEqual(result.lex, expected.lex)
            self.assertEqual(result.token_type, expected.token_type)

    def test_number(self):
        lexer = Lexer(eof="eof")
        input_text = "12345"
        expected_tokens = [Token("12345", "NUMBER"), Token("$", "eof")]

        result_tokens = lexer(input_text)
        self.assertEqual(
            len(result_tokens), len(expected_tokens), "Número incorrecto de tokens."
        )
        for result, expected in zip(result_tokens, expected_tokens):
            self.assertEqual(result.lex, expected.lex)
            self.assertEqual(result.token_type, expected.token_type)


if __name__ == "__main__":
    unittest.main()
