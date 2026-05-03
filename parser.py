import ply.yacc as yacc

from lexer import MiniFunLexer


class MiniFunParser:
    tokens = MiniFunLexer.tokens

    def __init__(self):
        self.lexer_obj = MiniFunLexer()
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)

    def parse(self, text):
        self.lexer_obj.lexer.lineno = 1
        return self.parser.parse(text, lexer=self.lexer_obj.lexer)

    def p_program(self, p):
        """program : program statement
                   | statement"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_statement_expression(self, p):
        "statement : expression SEMICOLON"
        p[0] = p[1]

    def p_statement_let(self, p):
        "statement : LET ID COLON type EQUALS expression SEMICOLON"
        p[0] = ("let", p[2], p[4], p[6])

    def p_statement_fun_decl(self, p):
        "statement : FUN ID COLON signature SEMICOLON"
        types = p[4]
        p[0] = ("fun_decl", p[2], types[:-1], types[-1])

    def p_statement_fun_def(self, p):
        "statement : LET ID param_list EQUALS expression SEMICOLON"
        p[0] = ("fun_def", p[2], p[3], p[5])

    def p_signature(self, p):
        "signature : type ARROW type_chain"
        p[0] = [p[1]] + p[3]

    def p_type_chain_recursive(self, p):
        "type_chain : type ARROW type_chain"
        p[0] = [p[1]] + p[3]

    def p_type_chain_single(self, p):
        "type_chain : type"
        p[0] = [p[1]]

    def p_param_list_recursive(self, p):
        "param_list : param_list ID"
        p[0] = p[1] + [p[2]]

    def p_param_list_single(self, p):
        "param_list : ID"
        p[0] = [p[1]]

    def p_type(self, p):
        """type : INT_TYPE
                | BOOL_TYPE
                | STRING_TYPE"""
        p[0] = p[1]

    def p_expression_if(self, p):
        "expression : IF expression THEN expression ELSE expression"
        p[0] = ("if", p[2], p[4], p[6])

    def p_expression_when(self, p):
        "expression : WHEN expression IS cases END"
        p[0] = ("when", p[2], p[4])

    def p_expression_comparison(self, p):
        "expression : comparison"
        p[0] = p[1]

    def p_comparison_binary(self, p):
        """comparison : additive LT additive
                      | additive GT additive
                      | additive GE additive
                      | additive LE additive
                      | additive EQ additive
                      | additive NEQ additive"""
        p[0] = ("binop", p[2], p[1], p[3])

    def p_comparison_additive(self, p):
        "comparison : additive"
        p[0] = p[1]

    def p_additive_binary(self, p):
        """additive : additive PLUS multiplicative
                    | additive MINUS multiplicative"""
        p[0] = ("binop", p[2], p[1], p[3])

    def p_additive_multiplicative(self, p):
        "additive : multiplicative"
        p[0] = p[1]

    def p_multiplicative_binary(self, p):
        """multiplicative : multiplicative TIMES unary
                          | multiplicative DIVIDE unary"""
        p[0] = ("binop", p[2], p[1], p[3])

    def p_multiplicative_unary(self, p):
        "multiplicative : unary"
        p[0] = p[1]

    def p_unary_minus(self, p):
        "unary : MINUS unary"
        p[0] = ("neg", p[2])

    def p_unary_application(self, p):
        "unary : application"
        p[0] = p[1]

    def p_application(self, p):
        "application : primary application_tail"
        if p[2]:
            p[0] = ("call", p[1], p[2])
        else:
            p[0] = p[1]

    def p_application_tail_recursive(self, p):
        "application_tail : atom application_tail"
        p[0] = [p[1]] + p[2]

    def p_application_tail_empty(self, p):
        "application_tail : empty"
        p[0] = []

    def p_primary_id(self, p):
        "primary : ID"
        p[0] = ("var", p[1])

    def p_primary_atom(self, p):
        "primary : atom"
        p[0] = p[1]

    def p_atom_number(self, p):
        "atom : NUMBER"
        p[0] = p[1]

    def p_atom_string(self, p):
        "atom : STRING"
        p[0] = p[1]

    def p_atom_true(self, p):
        "atom : TRUE"
        p[0] = True

    def p_atom_false(self, p):
        "atom : FALSE"
        p[0] = False

    def p_atom_group(self, p):
        "atom : LPAREN expression RPAREN"
        p[0] = p[2]

    def p_cases_recursive(self, p):
        "cases : cases case"
        p[0] = p[1] + [p[2]]

    def p_cases_single(self, p):
        "cases : case"
        p[0] = [p[1]]

    def p_case(self, p):
        "case : pattern_list ARROW expression SEMICOLON"
        p[0] = ("case", p[1], p[3])

    def p_pattern_list_recursive(self, p):
        "pattern_list : pattern_list COMMA pattern"
        p[0] = p[1] + [p[3]]

    def p_pattern_list_single(self, p):
        "pattern_list : pattern"
        p[0] = [p[1]]

    def p_pattern_number(self, p):
        "pattern : NUMBER"
        p[0] = p[1]

    def p_pattern_negative_number(self, p):
        "pattern : MINUS NUMBER"
        p[0] = -p[2]

    def p_pattern_true(self, p):
        "pattern : TRUE"
        p[0] = True

    def p_pattern_false(self, p):
        "pattern : FALSE"
        p[0] = False

    def p_pattern_string(self, p):
        "pattern : STRING"
        p[0] = p[1]

    def p_pattern_default(self, p):
        "pattern : UNDERSCORE"
        p[0] = ("wildcard",)

    def p_empty(self, p):
        "empty :"
        p[0] = None

    def p_error(self, p):
        if p:
            print(f"Linha {p.lineno}: erro de sintaxe perto de '{p.value}'")
        else:
            print("Erro de sintaxe no fim do ficheiro")
