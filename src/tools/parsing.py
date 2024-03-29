from itertools import islice
from src.cmp.utils import ContainerSet, Token


def compute_local_first(firsts, alpha):
    first_alpha = ContainerSet()

    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False

    ###################################################
    # alpha == epsilon ? First(alpha) = { epsilon }
    ###################################################
    if alpha_is_epsilon:
        first_alpha.set_epsilon()
    ###################################################

    ###################################################
    # alpha = X1 ... XN
    # First(Xi) subconjunto First(alpha)
    # epsilon pertenece a First(X1)...First(Xi) ? First(Xi+1) subconjunto de First(X) y First(alpha)
    # epsilon pertenece a First(X1)...First(XN) ? epsilon pertence a First(X) y al First(alpha)
    ###################################################
    else:
        for symbol in alpha:
            first_symbol = firsts[symbol]
            first_alpha.update(first_symbol)
            if not first_symbol.contains_epsilon:
                break
        else:
            first_alpha.set_epsilon()
    ###################################################

    # First(alpha)
    return first_alpha


def compute_firsts(G):
    firsts = {}
    change = True

    # init First(Vt)
    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)

    # init First(Vn)
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()

    while change:
        change = False

        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right

            # get current First(X)
            first_X = firsts[X]

            # init First(alpha)
            try:
                first_alpha = firsts[alpha]
            except KeyError:
                first_alpha = firsts[alpha] = ContainerSet()

            # CurrentFirst(alpha)???
            local_first = compute_local_first(firsts, alpha)

            # update First(X) and First(alpha) from CurrentFirst(alpha)
            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)

    # First(Vt) + First(Vt) + First(RightSides)
    return firsts


def compute_follows(G, firsts):
    follows = {}
    change = True

    # Inicializar Follow para cada no terminal con un conjunto vacío
    for nonterminal in G.nonTerminals:
        follows[nonterminal] = ContainerSet()
    # Añadir EOF al Follow del símbolo de inicio
    follows[G.startSymbol].add(G.EOF)

    while change:
        change = False

        # Para cada producción P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right

            # Follow actual de X para comparar después
            follow_X = follows[X]

            # Iterar a través de alpha buscando no terminales Y y calculando su Follow
            for i, B in enumerate(alpha):
                if B in G.nonTerminals:
                    # Inicialmente, no asumimos que epsilon está en First(beta)
                    beta_first = ContainerSet()

                    # Beta es la secuencia después del no terminal B
                    beta = islice(alpha, i + 1, None)

                    # Calcular First(beta) - {epsilon}
                    for symbol in beta:
                        symbol_first = firsts[symbol]
                        beta_first.hard_update(symbol_first)
                        if not symbol_first.contains_epsilon:
                            break
                    else:
                        # Si todos los símbolos en beta derivan en epsilon, o beta es vacío,
                        # agregamos Follow(X) a Follow(B)
                        beta_first.set_epsilon(False)
                        change |= follows[B].hard_update(follow_X)

                    # Actualizamos Follow(B) con First(beta) - {epsilon}
                    change |= follows[B].update(beta_first)

    return follows


def build_parsing_table(G, firsts, follows):
    # Inicializar la tabla de análisis
    M = {}

    # P: X -> alpha
    for production in G.Productions:
        X = production.Left
        alpha = production.Right

        # Trabajando con símbolos en First(alpha)...
        first_alpha = compute_local_first(firsts, alpha)
        for terminal in first_alpha:
            if not terminal.IsEpsilon:  # Asegurándose de no incluir epsilon
                M[(X, terminal)] = [
                    production
                ]  # Asumiendo que X tiene un atributo Name para su nombre

        # Trabajando con epsilon...
        if first_alpha.contains_epsilon:
            for terminal in follows[X]:
                # Asegúrate de incluir producciones donde epsilon está en First(alpha) y terminal está en Follow(X)
                if (
                    not terminal.IsEpsilon
                ):  # Asegurándose de no incluir epsilon como terminal
                    if (X, terminal) in M:
                        M[(X, terminal)].append(
                            production
                        )  # Agregar producción si ya existe entrada
                    else:
                        M[(X, terminal)] = [production]

                # Añadir la producción al símbolo EOF si es necesario
                if follows[
                    X
                ].contains_epsilon:  # Si Follow(X) contiene epsilon, considerarlo como '$'
                    M[(X, "EOF")] = [production]

    return M


def deprecated_metodo_predictivo_no_recursivo(G, M=None, firsts=None, follows=None):
    # Verificar tabla...
    if M is None:
        if firsts is None:
            firsts = compute_firsts(G)
        if follows is None:
            follows = compute_follows(G, firsts)
        M = build_parsing_table(G, firsts, follows)

    # Construcción del parser...
    def parser(w):
        # # w termina con $ (G.EOF)
        # w += (
        #     G.EOF
        # )  # Asegúrate de que la cadena de entrada termine con el símbolo de fin de archivo

        # Inicialización:
        stack = [
            G.EOF,
            G.startSymbol,
        ]  # La pila inicia con EOF y el símbolo de inicio de la gramática
        cursor = 0  # Posición actual en la cadena de entrada
        output = []  # Salida: derivación izquierda de la cadena de entrada

        # Analizando w...
        while stack:
            top = stack[-1]  # Observar (sin eliminar) el elemento en el tope de la pila
            a = w[cursor]  # Símbolo actual en la cadena de entrada
            if top == a == G.EOF:
                # Si el tope de la pila y el símbolo actual son EOF, el análisis ha terminado exitosamente
                break

            elif top in G.terminals:
                # Si el tope de la pila es un terminal, se compara con el símbolo actual de la entrada
                if top == a:
                    stack.pop()  # Eliminar el símbolo de la pila
                    cursor += 1  # Mover el cursor de la entrada
                else:
                    # Error: el símbolo de la entrada no coincide con el esperado
                    raise SyntaxError("Error de sintaxis")

            elif (top, a) in M:
                # Si hay una producción en M para el no terminal en el tope de la pila y el símbolo actual
                stack.pop()  # Eliminar el no terminal de la pila
                production = M[(top, a)]
                output.append(production)  # Añadir la producción a la salida

                # Empujar el lado derecho de la producción en la pila, en orden inverso
                for symbol in reversed(production[0].Right):
                    if not symbol.IsEpsilon:  # No empujar epsilon
                        stack.append(symbol)
            else:
                # Error: no hay producción aplicable
                raise SyntaxError("Error de sintaxis, no hay producción aplicable")
                # continue

        # El análisis izquierdo está listo!
        return [out[0] for out in output]

    return parser


def metodo_predictivo_no_recursivo(G, M=None):
    parser = deprecated_metodo_predictivo_no_recursivo(G, M)

    def updated(tokens):
        return parser([t.token_type for t in tokens])

    return updated


def evaluate_parse(left_parse, tokens):
    if not left_parse or not tokens:
        return

    left_parse = iter(left_parse)
    tokens = iter(tokens)
    result = evaluate(next(left_parse), left_parse, tokens)

    return result


def evaluate(production, left_parse, tokens, inherited_value=None):
    head, body = production
    attributes = production.attributes

    # Insert your code here ...
    synteticed = [None] * (len(body) + 1)
    inherited = [None] * (len(body) + 1)
    inherited[0] = inherited_value

    for i, symbol in enumerate(body, 1):
        if symbol.IsTerminal:
            assert inherited[i] is None
            synteticed[i] = next(tokens).lex
        else:
            next_production = next(left_parse)
            assert symbol == next_production.Left
            if attributes[i]:
                inherited[i] = attributes[i](inherited, synteticed)
            synteticed[i] = evaluate(next_production, left_parse, tokens, inherited[i])

    # Insert your code here ...
    if attributes[0]:
        synteticed[0] = attributes[0](inherited, synteticed)
    # > return ...
    return synteticed[0]


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
