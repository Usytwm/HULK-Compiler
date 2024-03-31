from src.cmp.pycompiler import Grammar
from src.cmp.pycompiler import Item
from src.cmp.utils import ContainerSet
from src.tools.parsing import compute_local_first, compute_firsts
from src.cmp.automata import multiline_formatter, State
import sys
import os

current_dir = os.getcwd()
sys.path.insert(0, current_dir)


class ShiftReduceParser:
    SHIFT = "SHIFT"
    REDUCE = "REDUCE"
    OK = "OK"

    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [0]
        cursor = 0
        output = []
        operations = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose:
                print(stack, w[cursor:])

            # Detect error
            try:
                action, tag = self.action[state, lookahead]
                # Shift case
                if action == ShiftReduceParser.SHIFT:
                    operations.append(ShiftReduceParser.SHIFT)
                    print(f"Shift: Tag: {tag} State: {state} Lookahead: {lookahead}")
                    stack.append(tag)
                    cursor += 1
                # Reduce case
                elif action == ShiftReduceParser.REDUCE:
                    print(f"Reduce: Tag: {tag} State: {state} Lookahead: {lookahead}")
                    for _ in range(len(tag.Right)):
                        stack.pop()
                    operations.append(ShiftReduceParser.REDUCE)
                    stack.append(self.goto[stack[-1], tag.Left])
                    output.append(tag)
                # OK case
                elif action == ShiftReduceParser.OK:
                    return output, operations
                # Invalid case
                else:
                    assert False, "Must be something wrong!"
            except KeyError:
                raise Exception("Aborting parsing, item is not viable.")

    def __iter__(self):
        # El iterador es el objeto mismo en este caso.
        return self

    def __next__(self):
        # Incrementar el contador.
        if self.actual < self.alto:
            num = self.actual
            self.actual += 1
            return num
        else:
            # No hay más elementos, detener la iteración.
            raise StopIteration


class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)

        automaton = build_LR1_automaton(G)
        for i, node in enumerate(automaton):
            if self.verbose:
                print(i, "\t", "\n\t ".join(str(x) for x in node.state), "\n")
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == G.startSymbol:
                        LR1Parser._register(
                            self.action, (idx, G.EOF), (ShiftReduceParser.OK, None)
                        )
                    else:
                        for lookahead in item.lookaheads:
                            LR1Parser._register(
                                self.action,
                                (idx, lookahead),
                                (ShiftReduceParser.REDUCE, prod),
                            )
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        LR1Parser._register(
                            self.action,
                            (idx, next_symbol),
                            (ShiftReduceParser.SHIFT, node[next_symbol.Name][0].idx),
                        )
                    else:
                        LR1Parser._register(
                            self.goto,
                            (idx, next_symbol),
                            node[next_symbol.Name][0].idx,
                        )
                pass

    @staticmethod
    def _register(table, key, value):
        assert (
            key not in table or table[key] == value
        ), "Shift-Reduce or Reduce-Reduce conflict!!!"
        table[key] = value


def expand(item, firsts):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []

    lookaheads = ContainerSet()
    # Compute lookahead for child items
    for preview in item.Preview():
        lookaheads.hard_update(compute_local_first(firsts, preview))

    assert not lookaheads.contains_epsilon
    # Build and return child items
    return [Item(prod, 0, lookaheads) for prod in next_symbol.productions]


def compress(items):
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)

    return {
        Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items()
    }


def closure_lr1(items, firsts):
    closure = ContainerSet(*items)

    changed = True
    while changed:
        changed = False

        new_items = ContainerSet()
        for item in closure:
            new_items.extend(expand(item, firsts))

        changed = closure.update(new_items)

    return compress(closure)


def goto_lr1(items, symbol, firsts=None, just_kernel=False):
    assert (
        just_kernel or firsts is not None
    ), "`firsts` must be provided if `just_kernel=False`"
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(items, firsts)


def build_LR1_automaton(G):
    assert len(G.startSymbol.productions) == 1, "Grammar must be augmented"

    firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])

    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in G.terminals + G.nonTerminals:
            # (Get/Build `next_state`)
            kernels = goto_lr1(current_state.state, symbol, just_kernel=True)

            if not kernels:
                continue

            try:
                next_state = visited[kernels]
            except KeyError:
                pending.append(kernels)
                visited[pending[-1]] = next_state = State(
                    frozenset(goto_lr1(current_state.state, symbol, firsts)), True
                )

            current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(multiline_formatter)
    return automaton
