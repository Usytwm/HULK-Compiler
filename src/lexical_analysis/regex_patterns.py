def build_regex():
    return [
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
            '"([^"])*"',
        ),
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
        ("exp", "(\^|\**)"),
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
    ]
