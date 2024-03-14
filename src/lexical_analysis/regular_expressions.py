from src.cmp.ast import AtomicNode, BinaryNode, RangeNode, UnaryNode
from src.cmp.pycompiler import Grammar
from src.tools.automatas import (
    DFA,
    NFA,
    automata_closure,
    automata_concatenation,
    automata_minimization,
    automata_union,
    nfa_to_dfa,
)

from src.cmp.utils import Token
from src.tools.parsing import evaluate_parse, metodo_predictivo_no_recursivo


class EpsilonNode(AtomicNode):
    def evaluate(self):
        return DFA(states=1, finals=[0], transitions={})


class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        return DFA(states=2, finals=[1], transitions={(0, s): 1})


class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value):
        return automata_closure(value)


class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_union(lvalue, rvalue)


class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_concatenation(lvalue, rvalue)


# def regex_tokenizer(text, G, skip_whitespaces=True):
#     tokens = []
#     # > fixed_tokens = ???
#     fixed_tokens = {lex: Token(lex, G[lex]) for lex in "| * + - ? ( ) [ ] ε".split()}
#     for char in text:
#         if skip_whitespaces and char.isspace():
#             continue
#         try:
#             tokens.append(fixed_tokens[char])
#         except KeyError:
#             tokens.append(Token(char, G["symbol"]))

#     tokens.append(Token("$", G.EOF))
#     return tokens


def regex_tokenizer(text, G, skip_whitespaces=True):
    tokens = []
    # > fixed_tokens = ???
    fixed_tokens = {lex: Token(lex, G[lex]) for lex in "| * + - ? ( ) [ ] ε".split()}

    literal = False

    for char in text:
        if literal:
            tokens.append(Token(char, G["symbol"]))
            literal = False
            continue

        if skip_whitespaces and char.isspace():
            continue

        if char == "\\":
            literal = True
            continue

        try:
            tokens.append(fixed_tokens[char])
        except KeyError:
            tokens.append(Token(char, G["symbol"]))

    tokens.append(Token("$", G.EOF))
    return tokens


def build_grammar():
    # G = Grammar()

    # E = G.NonTerminal("E", True)
    # T, F, A, X, Y, Z = G.NonTerminals("T F A X Y Z")
    # pipe, star, opar, cpar, symbol, epsilon = G.Terminals("| * ( ) symbol ε")

    # # > PRODUCTIONS???
    # E %= T + X, lambda h, s: s[2], None, lambda h, s: s[1]

    # X %= pipe + T + X, lambda h, s: s[3], None, None, lambda h, s: UnionNode(h[0], s[2])
    # X %= G.Epsilon, lambda h, s: h[0]

    # T %= F + Y, lambda h, s: s[2], None, lambda h, s: s[1]

    # Y %= F + Y, lambda h, s: s[2], None, lambda h, s: ConcatNode(h[0], s[1])
    # Y %= G.Epsilon, lambda h, s: h[0]

    # F %= A + Z, lambda h, s: s[2], None, lambda h, s: s[1]

    # Z %= star, lambda h, s: ClosureNode(h[0]), None
    # Z %= G.Epsilon, lambda h, s: h[0]

    # A %= epsilon, lambda h, s: EpsilonNode(s[1]), None
    # A %= symbol, lambda h, s: SymbolNode(s[1]), None
    # A %= opar + E + cpar, lambda h, s: s[2], None, None, None
    EPSILON = "ε"

    G = Grammar()

    E = G.NonTerminal("E", True)
    T, F, A, X, Y, Z, W, J = G.NonTerminals("T F A X Y Z W J")
    pipe, star, plus, minus, question, opar, cpar, obra, cbra, symbol, epsilon = (
        G.Terminals("| * + - ? ( ) [ ] symbol ε")
    )

    # > PRODUCTIONS???
    E %= T + X, lambda h, s: s[2], None, lambda h, s: s[1]

    X %= pipe + T + X, lambda h, s: s[3], None, None, lambda h, s: UnionNode(h[0], s[2])
    X %= G.Epsilon, lambda h, s: h[0]

    T %= F + Y, lambda h, s: s[2], None, lambda h, s: s[1]

    Y %= F + Y, lambda h, s: s[2], None, lambda h, s: ConcatNode(h[0], s[1])
    Y %= G.Epsilon, lambda h, s: h[0]

    F %= A + Z, lambda h, s: s[2], None, lambda h, s: s[1]

    Z %= star, lambda h, s: ClosureNode(h[0]), None
    Z %= plus, lambda h, s: ConcatNode(h[0], ClosureNode(h[0])), None
    Z %= question, lambda h, s: UnionNode(h[0], EpsilonNode(EPSILON)), None
    Z %= G.Epsilon, lambda h, s: h[0]

    A %= epsilon, lambda h, s: EpsilonNode(s[1]), None
    A %= symbol, lambda h, s: SymbolNode(s[1]), None
    A %= opar + E + cpar, lambda h, s: s[2], None, None, None
    A %= (
        obra + symbol + W + cbra,
        lambda h, s: s[3],
        None,
        None,
        lambda h, s: SymbolNode(s[2]),
        None,
    )

    W %= (
        symbol + W,
        lambda h, s: UnionNode(h[0], s[2]),
        None,
        lambda h, s: SymbolNode(s[1]),
    )
    W %= (
        minus + symbol + J,
        lambda h, s: s[3],
        None,
        None,
        lambda h, s: RangeNode(h[0], SymbolNode(s[2])),
    )
    W %= G.Epsilon, lambda h, s: h[0]

    J %= (
        symbol + W,
        lambda h, s: UnionNode(h[0], s[2]),
        None,
        lambda h, s: SymbolNode(s[1]),
    )
    J %= G.Epsilon, lambda h, s: h[0]

    return G


G = build_grammar()

L = metodo_predictivo_no_recursivo(G)


class Regex:
    def __init__(self, regex, skip_whitespaces=False):
        W = self
        W.regex = regex
        W.automaton = W.build_automaton(regex)

    def __call__(self, text):
        W = self
        return W.automaton.recognize(text)

    @staticmethod
    def build_automaton(regex, skip_whitespaces=False):
        h = regex_tokenizer(regex, G, skip_whitespaces=False)
        f = L(h)
        T = evaluate_parse(f, h)
        H = T.evaluate()
        X = nfa_to_dfa(H)
        k = automata_minimization(X)
        return k
