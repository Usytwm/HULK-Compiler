import pydot
from src.cmp.utils import ContainerSet, DisjointSet


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


class DFA(NFA):

    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)

        transitions = {key: [value] for key, value in transitions.items()}
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start

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


def move(automaton, states, symbol):
    moves = set()
    for state in states:
        try:
            moves.update(automaton.transitions[state][symbol])
        except KeyError:
            pass
    return moves


def epsilon_closure(automaton, states):
    pending = [s for s in states]
    closure = {s for s in states}

    while pending:
        state = pending.pop()
        for trans in automaton.epsilon_transitions(state):
            if not trans in closure:
                pending.append(trans)
                closure.add(trans)

    return ContainerSet(*closure)


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


def nfa_recognize(automaton, string):
    current = epsilon_closure(automaton, [automaton.start])
    for symbol in string:
        current = epsilon_closure(automaton, move(automaton, current, symbol))

    return any(s in automaton.finals for s in current)


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


def automata_intersection(a1, a2):
    return automata_complement(
        automata_union(automata_complement(a1), automata_complement(a2))
    )


def automata_difference(a1, a2):
    return automata_complement(automata_union(automata_complement(a1), a2))


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
