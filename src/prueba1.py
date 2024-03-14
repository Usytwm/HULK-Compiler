import pydot


class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = {state: {} for state in range(states)}

        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, "__iter__"), "Invalid collection of states"
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)

        self.vocabulary.discard("")

    def epsilon_transitions(self, state):
        assert state in self.transitions, "Invalid state"
        try:
            return self.transitions[state][""]
        except KeyError:
            return ()

    def graph(self):
        G = pydot.Dot(rankdir="LR", margin=0.1)
        G.add_node(pydot.Node("start", shape="plaintext", label="", width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = "ε" if tran == "" else tran
            G.add_node(
                pydot.Node(
                    start, shape="circle", style="bold" if start in self.finals else ""
                )
            )
            for end in destinations:
                G.add_node(
                    pydot.Node(
                        end, shape="circle", style="bold" if end in self.finals else ""
                    )
                )
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge("start", self.start, label="", style="dashed"))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode("utf8")
        except:
            pass


nfa = NFA(
    states=3, finals=[2], transitions={(0, "a"): [0], (0, "b"): [0, 1], (1, "a"): [2]}
)


class DFA(NFA):

    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)

        transitions = {key: [value] for key, value in transitions.items()}
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start

    def epsilon_transitions(self):
        raise TypeError()

    def _move(self, symbol):
        self.current = self.transitions[self.current][symbol][0]

    def _reset(self):
        self.current = self.start

    def recognize(self, string):
        self._reset()
        for symbol in string:
            try:
                self._move(symbol)
            except KeyError:
                return False

        return self.current in self.finals


automaton = DFA(
    states=3,
    finals=[2],
    transitions={
        (0, "a"): 0,
        (0, "b"): 1,
        (1, "a"): 2,
        (1, "b"): 1,
        (2, "a"): 0,
        (2, "b"): 1,
    },
)

assert automaton.recognize("ba")
assert automaton.recognize("aababbaba")

assert not automaton.recognize("")
assert not automaton.recognize("aabaa")
assert not automaton.recognize("aababb")


from cmp.utils import ContainerSet

automaton = NFA(
    states=6,
    finals=[3, 5],
    transitions={
        (0, ""): [1, 2],
        (1, ""): [3],
        (1, "b"): [4],
        (2, "a"): [4],
        (3, "c"): [3],
        (4, ""): [5],
        (5, "d"): [5],
    },
)


def move(automaton, states, symbol):
    moves = set()
    for state in states:
        try:
            moves.update(automaton.transitions[state][symbol])
        except KeyError:
            pass
    return moves


assert move(automaton, [1], "a") == set()
assert move(automaton, [2], "a") == {4}
assert move(automaton, [1, 5], "d") == {5}


def epsilon_closure(automaton, states):
    pending = list(states)
    closure = set(states)

    while pending:
        state = pending.pop()
        for trans in automaton.epsilon_transitions(state):
            if not trans in closure:
                pending.append(trans)
                closure.add(trans)

    return ContainerSet(*closure)


assert epsilon_closure(automaton, [0]) == {0, 1, 2, 3}
assert epsilon_closure(automaton, [0, 4]) == {0, 1, 2, 3, 4, 5}
assert epsilon_closure(automaton, [1, 2, 4]) == {1, 2, 3, 4, 5}


def nfa_to_dfa(automaton):
    transitions = {}

    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [start]

    pending = [start]
    while pending:
        state = pending.pop()

        for symbol in automaton.vocabulary:
            trans = epsilon_closure(automaton, move(automaton, state, symbol))

            if not trans:
                continue

            for s in states:
                if trans == s:
                    trans = s
                    break
            else:
                trans.id = len(states)
                trans.is_final = any(s in automaton.finals for s in trans)
                states.append(trans)
                pending.append(trans)

            try:
                transitions[state.id, symbol]
                assert False, "Invalid DFA!!!"
            except KeyError:
                transitions[state.id, symbol] = trans.id

    finals = [state.id for state in states if state.is_final]
    dfa = DFA(len(states), finals, transitions)

    return dfa


dfa = nfa_to_dfa(automaton)

assert dfa.states == 4
assert len(dfa.finals) == 4

assert dfa.recognize("")
assert dfa.recognize("a")
assert dfa.recognize("b")
assert dfa.recognize("cccccc")
assert dfa.recognize("adddd")
assert dfa.recognize("bdddd")

assert not dfa.recognize("dddddd")
assert not dfa.recognize("cdddd")
assert not dfa.recognize("aa")
assert not dfa.recognize("ab")
assert not dfa.recognize("ddddc")


automaton = NFA(
    states=3,
    finals=[2],
    transitions={
        (0, "a"): [0],
        (0, "b"): [0, 1],
        (1, "a"): [2],
        (1, "b"): [2],
    },
)

print(
    "Lenguaje de las cadenas sobre {a, b}* tal que su penultimo simbolo es `b`, en leguaje regular: (a|b)*b(a|b)"
)


assert move(automaton, [0, 1], "a") == {0, 2}
assert move(automaton, [0, 1], "b") == {0, 1, 2}

dfa = nfa_to_dfa(automaton)

assert dfa.states == 4
assert len(dfa.finals) == 2

assert dfa.recognize("aba")
assert dfa.recognize("bb")
assert dfa.recognize("aaaaaaaaaaaba")

assert not dfa.recognize("aaa")
assert not dfa.recognize("ab")
assert not dfa.recognize("b")
assert not dfa.recognize("")

automaton = NFA(
    states=5,
    finals=[4],
    transitions={
        (0, "a"): [0, 1],
        (0, "b"): [0, 2],
        (0, "c"): [0, 3],
        (1, "a"): [1, 4],
        (1, "b"): [1],
        (1, "c"): [1],
        (2, "a"): [2],
        (2, "b"): [2, 4],
        (2, "c"): [2],
        (3, "a"): [3],
        (3, "b"): [3],
        (3, "c"): [3, 4],
    },
)

print("Lenguaje de las cadenas sobre {a, b, c}* tales que el ultimo simbolo se repite,")
print("en lenguaje regular: ([a-c]*a[a-c]*a) | ([a-c]*b[a-c]*b) | ([a-c]*c[a-c]*c) .")

dfa = nfa_to_dfa(automaton)

assert dfa.states == 15
assert len(dfa.finals) == 7

assert dfa.recognize("abccac")
assert dfa.recognize("bbbbbbbbaa")
assert dfa.recognize("cac")

assert not dfa.recognize("abbbbc")
assert not dfa.recognize("a")
assert not dfa.recognize("")
assert not dfa.recognize("acacacaccab")


def nfa_recognize(automaton, string):
    current = epsilon_closure(automaton, [automaton.start])
    for symbol in string:
        current = epsilon_closure(automaton, move(automaton, current, symbol))

    return any(s in automaton.finals for s in current)


automaton = NFA(
    states=6,
    finals=[3, 5],
    transitions={
        (0, ""): [1, 2],
        (1, ""): [3],
        (1, "b"): [4],
        (2, "a"): [4],
        (3, "c"): [3],
        (4, ""): [5],
        (5, "d"): [5],
    },
)

assert nfa_recognize(automaton, "")
assert nfa_recognize(automaton, "a")
assert nfa_recognize(automaton, "b")
assert nfa_recognize(automaton, "cccccc")
assert nfa_recognize(automaton, "adddd")
assert nfa_recognize(automaton, "bdddd")

assert not nfa_recognize(automaton, "dddddd")
assert not nfa_recognize(automaton, "cdddd")
assert not nfa_recognize(automaton, "aa")
assert not nfa_recognize(automaton, "ab")
assert not nfa_recognize(automaton, "ddddc")

automaton = NFA(
    states=3,
    finals=[2],
    transitions={
        (0, "a"): [0],
        (0, "b"): [0, 1],
        (1, "a"): [2],
        (1, "b"): [2],
    },
)

assert nfa_recognize(automaton, "aba")
assert nfa_recognize(automaton, "bb")
assert nfa_recognize(automaton, "aaaaaaaaaaaba")

assert not nfa_recognize(automaton, "aaa")
assert not nfa_recognize(automaton, "ab")
assert not nfa_recognize(automaton, "b")
assert not nfa_recognize(automaton, "")

automaton = NFA(
    states=5,
    finals=[4],
    transitions={
        (0, "a"): [0, 1],
        (0, "b"): [0, 2],
        (0, "c"): [0, 3],
        (1, "a"): [1, 4],
        (1, "b"): [1],
        (1, "c"): [1],
        (2, "a"): [2],
        (2, "b"): [2, 4],
        (2, "c"): [2],
        (3, "a"): [3],
        (3, "b"): [3],
        (3, "c"): [3, 4],
    },
)

assert nfa_recognize(automaton, "abccac")
assert nfa_recognize(automaton, "bbbbbbbbaa")
assert nfa_recognize(automaton, "cac")

assert not nfa_recognize(automaton, "abbbbc")
assert not nfa_recognize(automaton, "a")
assert not nfa_recognize(automaton, "")
assert not nfa_recognize(automaton, "acacacaccab")


automaton = DFA(
    states=2,
    finals=[1],
    transitions={
        (0, "a"): 0,
        (0, "b"): 1,
        (1, "a"): 0,
        (1, "b"): 1,
    },
)


def automata_union(a1, a2):
    transitions = {}

    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        transitions[origin + d1, symbol] = [state + d1 for state in destinations]

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        transitions[origin + d2, symbol] = [state + d2 for state in destinations]

    ## Add transitions from start state ...
    transitions[start, ""] = [d1, d2]

    ## Add transitions to final state ...
    for state in a1.finals:
        try:
            transitions[state + d1, ""].append(final)
        except KeyError:
            transitions[state + d1, ""] = [final]

    for state in a2.finals:
        try:
            transitions[state + d2, ""].append(final)
        except KeyError:
            transitions[state + d2, ""] = [final]

    states = a1.states + a2.states + 2
    finals = {final}

    return NFA(states, finals, transitions, start)


union = automata_union(automaton, automaton)
recognize = nfa_to_dfa(union).recognize

assert union.states == 2 * automaton.states + 2

assert recognize("b")
assert recognize("abbb")
assert recognize("abaaababab")

assert not recognize("")
assert not recognize("a")
assert not recognize("abbbbaa")


def automata_concatenation(a1, a2):
    transitions = {}

    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        transitions[origin + d1, symbol] = [state + d1 for state in destinations]

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        transitions[origin + d2, symbol] = [state + d2 for state in destinations]

    ## Add transitions from start state ...
    for state in a1.finals:
        try:
            transitions[state, ""].append(d2)
        except KeyError:
            transitions[state, ""] = [d2]

    ## Add transitions to final state ...
    for state in a2.finals:
        try:
            transitions[state + d2, ""].append(final)
        except KeyError:
            transitions[state + d2, ""] = [final]

    states = a1.states + a2.states + 1
    finals = {final}

    return NFA(states, finals, transitions, a1.start)


concat = automata_concatenation(automaton, automaton)
recognize = nfa_to_dfa(concat).recognize

assert concat.states == 2 * automaton.states + 1

assert recognize("bb")
assert recognize("abbb")
assert recognize("abaaababab")

assert not recognize("")
assert not recognize("a")
assert not recognize("b")
assert not recognize("ab")
assert not recognize("aaaab")
assert not recognize("abbbbaa")


def automata_closure(a1):
    transitions = {}

    start = 0
    d1 = 1
    final = a1.states + d1

    for (origin, symbol), destinations in a1.map.items():
        ## Relocate automaton transitions ...
        transitions[origin + d1, symbol] = [state + d1 for state in destinations]

    ## Add transitions from start state ...
    transitions[start, ""] = [d1, final]

    ## Add transitions to final state and to start state ...
    for state in a1.finals:
        try:
            transitions[state + d1, ""].append(final)
        except KeyError:
            transitions[state + d1, ""] = [final]

    transitions[final, ""] = [start]

    states = a1.states + 2
    finals = {final}

    return NFA(states, finals, transitions, start)


closure = automata_closure(automaton)
recognize = nfa_to_dfa(closure).recognize

assert closure.states == automaton.states + 2

assert recognize("")
assert recognize("b")
assert recognize("ab")
assert recognize("bb")
assert recognize("abbb")
assert recognize("abaaababab")

assert not recognize("a")
assert not recognize("abbbbaa")

from cmp.utils import DisjointSet

dset = DisjointSet(*range(10))
print("> Inicializando conjuntos disjuntos:\n", dset)

dset.merge([5, 9])
print("> Mezclando conjuntos 5 y 9:\n", dset)

dset.merge([8, 0, 2])
print("> Mezclando conjuntos 8, 0 y 2:\n", dset)

dset.merge([2, 9])
print("> Mezclando conjuntos 2 y 9:\n", dset)

print("> Representantes:\n", dset.representatives)
print("> Grupos:\n", dset.groups)
print("> Conjunto 0:\n", dset[0], "--->", type(dset[0]))
print("> Conjunto 0 [valor]:\n", dset[0].value, "--->", type(dset[0].value))
print(
    "> Conjunto 0 [representante]:\n",
    dset[0].representative,
    "--->",
    type(dset[0].representative),
)

automaton = DFA(
    states=5,
    finals=[4],
    transitions={
        (0, "a"): 1,
        (0, "b"): 2,
        (1, "a"): 1,
        (1, "b"): 3,
        (2, "a"): 1,
        (2, "b"): 2,
        (3, "a"): 1,
        (3, "b"): 4,
        (4, "a"): 1,
        (4, "b"): 2,
    },
)


def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:
        for prt in split.keys():
            for symbol in vocabulary:
                try:
                    t_member = automaton.transitions[member.value][symbol][0]
                    t_member = partition[t_member].representative
                except KeyError:
                    t_member = -1
                try:
                    t_prt = automaton.transitions[prt][symbol][0]
                    t_prt = partition[t_prt].representative
                except KeyError:
                    t_prt = -1
                if not t_member == t_prt:
                    break
            else:
                split[prt].append(member.value)
                break
        else:
            split[member.value] = [member.value]

    return [group for group in split.values()]


def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))

    ## partition = { NON-FINALS | FINALS }
    if len(automaton.finals) < automaton.states - 1:
        partition.merge(
            [
                state
                for state in range(automaton.states)
                if not state in automaton.finals
            ]
        )
    if len(automaton.finals) > 1:
        partition.merge(list(automaton.finals))

    while True:
        new_partition = DisjointSet(*range(automaton.states))

        ## Split each group if needed (use distinguish_states(group, automaton, partition))
        for group in partition.groups:
            for new_group in distinguish_states(group, automaton, partition):
                if len(new_group) > 1:
                    new_partition.merge(new_group)

        if len(new_partition) == len(partition):
            break

        partition = new_partition

    return partition


def automata_minimization(automaton):
    partition = state_minimization(automaton)

    states = [s for s in partition.representatives]

    transitions = {}
    for i, state in enumerate(states):
        ## origin = ???
        origin = state.value
        for symbol, destinations in automaton.transitions[origin].items():
            trans = states.index(partition[destinations[0]].representative)

            try:
                transitions[i, symbol]
                assert False
            except KeyError:
                transitions[i, symbol] = trans

    ## finals = ???
    ## start  = ???
    finals = [i for i in range(len(states)) if states[i].value in automaton.finals]
    start = states.index(partition[automaton.start].representative)

    return DFA(len(states), finals, transitions, start)


mini = automata_minimization(automaton)

assert mini.states == 4

assert mini.recognize("abb")
assert mini.recognize("ababbaabb")

assert not mini.recognize("")
assert not mini.recognize("ab")
assert not mini.recognize("aaaaa")
assert not mini.recognize("bbbbb")
assert not mini.recognize("abbabababa")


# (a|b)*b
automaton = DFA(
    states=2,
    finals=[1],
    transitions={
        (0, "a"): 0,
        (0, "b"): 1,
        (1, "a"): 0,
        (1, "b"): 1,
    },
)

# (a|b)*abb
automaton2 = DFA(
    states=5,
    finals=[4],
    transitions={
        (0, "a"): 1,
        (0, "b"): 2,
        (1, "a"): 1,
        (1, "b"): 3,
        (2, "a"): 1,
        (2, "b"): 2,
        (3, "a"): 1,
        (3, "b"): 4,
        (4, "a"): 1,
        (4, "b"): 2,
    },
)


# Complemento, si el automata no es un DFA lo convertimos
def automata_complement(a1):
    if not isinstance(a1, DFA):
        a1 = nfa_to_dfa(a1)

    transitions = {}

    drain = None

    finals = []

    for (origin, symbol), destinations in a1.map.items():
        ## Copy automaton transitions ...
        transitions[origin, symbol] = [state for state in destinations]

    ## Add transitions to drain state ...
    for state in range(a1.states):
        for symbol in a1.vocabulary:
            try:
                transitions[state, symbol]
            except KeyError:
                drain = a1.states
                transitions[state, symbol] = [drain]

        if not state in a1.finals:
            finals.append(state)

    ## Add transitions from drain state ...
    if drain:
        finals.append(drain)
        for symbol in a1.vocabulary:
            transitions[drain, symbol] = [drain]
        states = a1.states + 1
    else:
        states = a1.states

    return NFA(states, finals, transitions, a1.start)


complement = automata_complement(automaton)
recognize = nfa_to_dfa(complement).recognize

assert complement.states == automaton.states

assert recognize("")
assert recognize("a")
assert recognize("aba")
assert recognize("bbba")
assert recognize("ababa")
assert recognize("babababa")

assert not recognize("b")
assert not recognize("ab")
assert not recognize("aab")
assert not recognize("bbab")
assert not recognize("ababb")
assert not recognize("bababb")
assert not recognize("aaaaaab")


def automata_intersection(a1, a2):
    return automata_complement(
        automata_union(automata_complement(a1), automata_complement(a2))
    )


intersection = automata_intersection(automaton, automaton2)
recognize = nfa_to_dfa(intersection).recognize

assert recognize("abb")
assert recognize("ababbaabb")

assert not recognize("")
assert not recognize("ab")
assert not recognize("aaaaa")
assert not recognize("bbbbb")
assert not recognize("abbabababa")


def automata_difference(a1, a2):
    return automata_complement(automata_union(automata_complement(a1), a2))


difference = automata_difference(automaton, automaton2)
recognize = nfa_to_dfa(difference).recognize

assert recognize("b")
assert recognize("bb")
assert recognize("aab")
assert recognize("bababbab")
assert recognize("aaaabbbbab")
assert recognize("aaaaaaaaaaaaaab")
assert recognize("bbbbbbbbbbbbbbbbb")
assert recognize("aaaaaaaaabbbbbb")

assert not recognize("a")
assert not recognize("aaaaa")
assert not recognize("bbbbbabba")
assert not recognize("abbabababa")
assert not recognize("abbababababb")
assert not recognize("abbababbbbababb")
assert not recognize("abbaabb")


# Reverso
def automata_reverse(a1):
    transitions = {}

    start = 0
    d1 = 1
    final = a1.start + d1

    for (origin, symbol), destinations in a1.map.items():
        ## Reverse automaton transitions ...
        for dest in destinations:
            try:
                transitions[dest + d1, symbol].append(origin + d1)
            except KeyError:
                transitions[dest + d1, symbol] = [origin + d1]

    ## Add transitions from start state ...
    for state in a1.finals:
        try:
            transitions[start, ""].append(state + d1)
        except KeyError:
            transitions[start, ""] = [state + d1]

    states = a1.states + 1

    finals = [final]

    return NFA(states, finals, transitions, start)


reverse = automata_reverse(automaton)
recognize = nfa_to_dfa(reverse).recognize

assert reverse.states == automaton.states + 1

assert recognize("b")
assert recognize("ba")
assert recognize("baa")
assert recognize("babb")
assert recognize("bbaba")
assert recognize("bbabab")
assert recognize("baaaaaa")

assert not recognize("")
assert not recognize("a")
assert not recognize("aba")
assert not recognize("abbb")
assert not recognize("ababa")
assert not recognize("ababababa")


class Node:
    def evaluate(self):
        raise NotImplementedError()


class AtomicNode(Node):
    def __init__(self, lex):
        self.lex = lex


class UnaryNode(Node):
    def __init__(self, node):
        self.node = node

    def evaluate(self):
        value = self.node.evaluate()
        return self.operate(value)

    @staticmethod
    def operate(value):
        raise NotImplementedError()


class BinaryNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        lvalue = self.left.evaluate()
        rvalue = self.right.evaluate()
        return self.operate(lvalue, rvalue)

    @staticmethod
    def operate(lvalue, rvalue):
        raise NotImplementedError()


from cmp.ast import get_printer

printer = get_printer(AtomicNode=AtomicNode, UnaryNode=UnaryNode, BinaryNode=BinaryNode)

EPSILON = "ε"


class EpsilonNode(AtomicNode):
    def evaluate(self):
        return DFA(states=1, finals=[0], transitions={})


EpsilonNode(EPSILON).evaluate()


class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        return DFA(states=2, finals=[1], transitions={(0, s): 1})


SymbolNode("a").evaluate()


class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value):
        return automata_closure(value)


ClosureNode(SymbolNode("a")).evaluate()


class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_union(lvalue, rvalue)


UnionNode(SymbolNode("a"), SymbolNode("b")).evaluate()


class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_concatenation(lvalue, rvalue)


ConcatNode(SymbolNode("a"), SymbolNode("b")).evaluate()

from cmp.pycompiler import Grammar

G = Grammar()

E = G.NonTerminal("E", True)
T, F, A, X, Y, Z = G.NonTerminals("T F A X Y Z")
pipe, star, opar, cpar, symbol, epsilon = G.Terminals("| * ( ) symbol ε")

# > PRODUCTIONS???
E %= T + X, lambda h, s: s[2], None, lambda h, s: s[1]

X %= pipe + T + X, lambda h, s: s[3], None, None, lambda h, s: UnionNode(h[0], s[2])
X %= G.Epsilon, lambda h, s: h[0]

T %= F + Y, lambda h, s: s[2], None, lambda h, s: s[1]

Y %= F + Y, lambda h, s: s[2], None, lambda h, s: ConcatNode(h[0], s[1])
Y %= G.Epsilon, lambda h, s: h[0]

F %= A + Z, lambda h, s: s[2], None, lambda h, s: s[1]

Z %= star, lambda h, s: ClosureNode(h[0]), None
Z %= G.Epsilon, lambda h, s: h[0]

A %= epsilon, lambda h, s: EpsilonNode(s[1]), None
A %= symbol, lambda h, s: SymbolNode(s[1]), None
A %= opar + E + cpar, lambda h, s: s[2], None, None, None

print(G)
from cmp.utils import Token


def regex_tokenizer(text, G, skip_whitespaces=True):
    tokens = []
    # > fixed_tokens = ???
    fixed_tokens = {lex: Token(lex, G[lex]) for lex in "| * ( ) ε".split()}
    for char in text:
        if skip_whitespaces and char.isspace():
            continue
        try:
            tokens.append(fixed_tokens[char])
        except KeyError:
            tokens.append(Token(char, G["symbol"]))

    tokens.append(Token("$", G.EOF))
    return tokens


tokens = regex_tokenizer("a*(a|b)*cd | ε", G)
print(tokens)

from prueba import metodo_predictivo_no_recursivo

parser = metodo_predictivo_no_recursivo(G)
left_parse = parser(tokens)


from prueba import evaluate_parse

ast = evaluate_parse(left_parse, tokens)
print(printer(ast))

nfa = ast.evaluate()
dfa = nfa_to_dfa(nfa)

assert dfa.recognize("")
assert dfa.recognize("cd")
assert dfa.recognize("aaaaacd")
assert dfa.recognize("bbbbbcd")
assert dfa.recognize("bbabababcd")
assert dfa.recognize("aaabbabababcd")

assert not dfa.recognize("cda")
assert not dfa.recognize("aaaaa")
assert not dfa.recognize("bbbbb")
assert not dfa.recognize("ababba")
assert not dfa.recognize("cdbaba")
assert not dfa.recognize("cababad")
assert not dfa.recognize("bababacc")

mini = automata_minimization(dfa)


class RangeNode(BinaryNode):
    def evaluate(self):
        return self.operate(self.left.lex, self.right.lex)

    @staticmethod
    def operate(lvalue, rvalue):
        a = ord(lvalue)
        b = ord(rvalue) + 1
        return DFA(
            states=2, finals=[1], transitions={(0, chr(asc)): 1 for asc in range(a, b)}
        )


RangeNode(SymbolNode("a"), SymbolNode("c")).evaluate()


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

W %= symbol + W, lambda h, s: UnionNode(h[0], s[2]), None, lambda h, s: SymbolNode(s[1])
W %= (
    minus + symbol + J,
    lambda h, s: s[3],
    None,
    None,
    lambda h, s: RangeNode(h[0], SymbolNode(s[2])),
)
W %= G.Epsilon, lambda h, s: h[0]

J %= symbol + W, lambda h, s: UnionNode(h[0], s[2]), None, lambda h, s: SymbolNode(s[1])
J %= G.Epsilon, lambda h, s: h[0]

print(G)


def regex_tokenizer(text, G, skip_whitespaces=True):
    tokens = []
    # > fixed_tokens = ???
    fixed_tokens = {lex: Token(lex, G[lex]) for lex in "| * + - ? ( ) [ ] ε".split()}
    for char in text:
        if skip_whitespaces and char.isspace():
            continue
        try:
            tokens.append(fixed_tokens[char])
        except KeyError:
            tokens.append(Token(char, G["symbol"]))

    tokens.append(Token("$", G.EOF))
    return tokens


# Probemos con los numeros no negativos de coma flotante
tokens = regex_tokenizer("([1-9][0-9]*|0)(.[0-9]+)?", G)


parser = metodo_predictivo_no_recursivo(G)
left_parse = parser(tokens)

ast = evaluate_parse(left_parse, tokens)
print(printer(ast))


nfa = ast.evaluate()

dfa = nfa_to_dfa(nfa)

assert dfa.recognize("1")
assert dfa.recognize("0")
assert dfa.recognize("12")
assert dfa.recognize("0.9999")
assert dfa.recognize("1234.5678")
assert dfa.recognize("2018")
assert dfa.recognize("87.090876")
assert dfa.recognize("87.0")
assert dfa.recognize("78.1")
assert dfa.recognize("3.1415")

assert not dfa.recognize("")
assert not dfa.recognize("0178")
assert not dfa.recognize("90.")
assert not dfa.recognize("3..1415")
assert not dfa.recognize(".2018")
assert not dfa.recognize("daniel")
assert not dfa.recognize("a123")


mini = automata_minimization(dfa)

# Probemos ahora con los identificadores de una variable
tokens = regex_tokenizer("[a-zA-Z][a-zA-Z0-9]*", G)

parser = metodo_predictivo_no_recursivo(G)
left_parse = parser(tokens)


ast = evaluate_parse(left_parse, tokens)
print(printer(ast))

nfa = ast.evaluate()


dfa = nfa_to_dfa(nfa)

assert dfa.recognize("a")
assert dfa.recognize("i")
assert dfa.recognize("j")
assert dfa.recognize("cont1")
assert dfa.recognize("year2019")
assert dfa.recognize("aaaaaaaaa00000aaja0ja0a90sdasaja8ja8ja8aj")
assert dfa.recognize("daniel")
assert dfa.recognize("b78")
assert dfa.recognize("c4m1n0r34l")
assert dfa.recognize("conker04")

assert not dfa.recognize("")
assert not dfa.recognize("0daniel")
assert not dfa.recognize("9898sdasdnla")
assert not dfa.recognize("++i")
assert not dfa.recognize("j++")
assert not dfa.recognize("j+=89")
assert not dfa.recognize("2^3")


mini = automata_minimization(dfa)

# Probemos con los numeros no negativos de coma flotante
tokens = regex_tokenizer("([1-9][0-9]*|0)(.[0-9]+)?", G)


parser = metodo_predictivo_no_recursivo(G)
left_parse = parser(tokens)

ast = evaluate_parse(left_parse, tokens)


nfa = ast.evaluate()

dfa = nfa_to_dfa(nfa)

# Probemos ahora con los identificadores de una variable
tokens = regex_tokenizer("[a-zA-Z][a-zA-Z0-9]*", G)

parser = metodo_predictivo_no_recursivo(G)
left_parse = parser(tokens)


ast = evaluate_parse(left_parse, tokens)
print(printer(ast))

nfa = ast.evaluate()


dfa = nfa_to_dfa(nfa)
mini = automata_minimization(dfa)
