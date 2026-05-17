import ply.lex as lex


class MiniFunLexer:
    tokens = (
        "NUMBER",
        "ID",
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "LT",
        "GT",
        "EQ",
        "NEQ",
        "GE",
        "LE",
        "EQUALS",
        "COLON",
        "COMMA",
        "UNDERSCORE",
        "SEMICOLON",
        "LPAREN",
        "RPAREN",
        "ARROW",
        "LET",
        "FUN",
        "IF",
        "THEN",
        "ELSE",
        "WHEN",
        "IS",
        "END",
        "INT_TYPE",
        "BOOL_TYPE",
        "TRUE",
        "FALSE",
    )

    reserved = {
        "let": "LET",
        "fun": "FUN",
        "if": "IF",
        "then": "THEN",
        "else": "ELSE",
        "when": "WHEN",
        "is": "IS",
        "end": "END",
        "Int": "INT_TYPE",
        "Bool": "BOOL_TYPE",
        "true": "TRUE",
        "false": "FALSE",
    }

    t_ignore = " \t\r"

    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_TIMES = r"\*"
    t_DIVIDE = r"/"

    t_EQ = r"=="
    t_NEQ = r"!="
    t_GE = r">="
    t_LE = r"<="
    t_LT = r"<"
    t_GT = r">"

    t_EQUALS = r"="
    t_COLON = r":"
    t_COMMA = r","
    t_SEMICOLON = r";"

    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_ARROW = r"->"

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_NUMBER(self, t):
        r"\d+"
        t.value = int(t.value)
        return t

    def t_UNDERSCORE(self, t):
        r"_"
        return t

    def t_ID(self, t):
        r"[a-zA-Z][a-zA-Z_0-9]*"
        t.type = self.reserved.get(t.value, "ID")
        return t

    def t_COMMENT_MULTILINE(self, t):
        r"\{-[\s\S]*?-\}"
        t.lexer.lineno += t.value.count("\n")

    def t_COMMENT(self, t):
        r"--[^\n]*"
        pass

    def t_error(self, t):
        raise SyntaxError(f"Linha {t.lineno}: caractere ilegal '{t.value[0]}'")

    def test(self, text):
        self.lexer.lineno = 1
        self.lexer.input(text)
        for tok in self.lexer:
            print(tok)
