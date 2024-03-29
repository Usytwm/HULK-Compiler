def build_regex():
    


    return [
        # numeros
        ("number", "(\-|\+)?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][\+\-]?[0-9]+)?"),
        # Espacios (para ser ignorados o manejados específicamente)
        ("space", " *"), # tacto
        # Nueva línea
        ("newline", "\n"), #tacto
        # Operadores de asignación y definición
        ("Equal", "="),
        ("Destroy", ":="),
        ("Colon", ":"),
        ("underscore", "_"), #tacto
        ("Arrow", "=>"),
        # Operadores de comparación
        ("Less", "<"),
        ("LessEqual", "<="),
        ("Greater", ">"),
        ("GreaterEqual", ">="),
        ("CompEqual", "=="),
        ("NotEqual", "!="),
        # Palabras clave
        ("Print", "print"),
        ("If", "if"),
        ("Else", "else"),
        ("Let", "let"),
        ("In", "in"),
        ("For", "for"),
        ("Function", "function"),
        ("Type", "type"),
        #("range", "range"),
        #("protocol", "protocol"),
        # Otros tokens especiales (como el operador de concatenación @)
        ("arroba", "@"),
        # Funciones matemáticas y constantes
        #("math_func", "(sin|cos|tan|log|sqrt|rand|exp)"),
        ("sqrt", 'sqrt'),
        ("sin", 'sin'),
        ("cos", 'cos'),
        ("tan", 'tan'),
        ("exp", 'exp'),
        ("log", 'log'),
        ("rand", 'rand'),
        ("pi", "PI"),
        # Identificadores
        ("identifier", "[a-zA-Z_][a-zA-Z0-9_]*"),
        # Cadenas de texto (incluyendo caracteres especiales)
        (
            "lit",
            '"([^"])*"',
        ),
        # Signos de puntuacion
        ("Dot", "\."),
        ("obracket", "\["),
        ("cbracket", "\]"),
        ("oBrace", "\{"),
        ("cBrace", "\}"),
        ("Plus", "\+"),
        ("Minus", "\-"),
        ("Mult", "\*"),
        ("Div", "\/"),
        ("exp", "(\^|\**)"),
        #("assign", "="),
        #("lt", "<"),
        #("gt", ">"),
        ("excl", "!"),
        ("amp", "&"),
        ("pipe", "\|"),
        ("tilde", "~"),
        ("Mod", "%"),
        ("oPar", "\("),
        ("cPar", "\)"),
        ("Semi", ";"),
        ("Comma", ","),
    ]

 