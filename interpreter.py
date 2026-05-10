class Interpreter:
    def __init__(self):
        self.env = {}
        self.env_types = {}
        self.functions = {}
        self.signatures = {}
        self.call_stack = []

    def get_type(self, value):
        if type(value) is bool:
            return "Bool"
        if type(value) is int:
            return "Int"
        return "Unknown"

    def resolve_variable_type(self, name, local_types):
        if local_types and name in local_types:
            return local_types[name]
        if name in self.env_types:
            return self.env_types[name]
        raise Exception(f"Erro Semântico: variável '{name}' não definida")

    def resolve_function_name(self, node):
        if isinstance(node, tuple) and node[0] == "var":
            return node[1]
        raise Exception("Erro Semântico: só identificadores de função podem ser aplicados")

    def is_wildcard(self, pattern):
        return isinstance(pattern, tuple) and pattern == ("wildcard",)

    def infer_type(self, node, local_types=None):
        if type(node) is bool:
            return "Bool"
        if type(node) is int:
            return "Int"

        kind = node[0]

        if kind == "var":
            return self.resolve_variable_type(node[1], local_types)

        if kind == "neg":
            value_type = self.infer_type(node[1], local_types)
            if value_type != "Int":
                raise Exception("Erro Semântico: o operador unário '-' só pode ser usado com Int")
            return "Int"

        if kind == "binop":
            _, op, left_node, right_node = node
            left_type = self.infer_type(left_node, local_types)
            right_type = self.infer_type(right_node, local_types)

            if op in {"+", "-", "*", "/"}:
                if left_type != "Int" or right_type != "Int":
                    raise Exception(
                        "Erro Semântico: operações aritméticas só aceitam operandos do tipo Int"
                    )
                return "Int"

            if op in {"<", ">", ">=", "<="}:
                if left_type != "Int" or right_type != "Int":
                    raise Exception(
                        "Erro Semântico: comparações ordenadas só aceitam operandos do tipo Int"
                    )
                return "Bool"

            if op in {"==", "!="}:
                if left_type != right_type:
                    raise Exception(
                        "Erro Semântico: comparação entre valores de tipos incompatíveis"
                    )
                return "Bool"

        if kind == "if":
            _, cond_node, then_node, else_node = node
            cond_type = self.infer_type(cond_node, local_types)
            then_type = self.infer_type(then_node, local_types)
            else_type = self.infer_type(else_node, local_types)

            if cond_type != "Bool":
                raise Exception("Erro Semântico: a condição do if tem de ser Bool")
            if then_type != else_type:
                raise Exception(
                    "Erro Semântico: os dois ramos do if têm de produzir valores do mesmo tipo"
                )
            return then_type

        if kind == "when":
            _, subject_node, cases = node
            subject_type = self.infer_type(subject_node, local_types)
            result_type = None

            for _, patterns, expr in cases:
                for pattern in patterns:
                    if self.is_wildcard(pattern):
                        continue
                    pattern_type = self.get_type(pattern)
                    if pattern_type != subject_type:
                        raise Exception(
                            "Erro Semântico: padrão do when incompatível com o tipo da expressão analisada"
                        )

                case_type = self.infer_type(expr, local_types)
                if result_type is None:
                    result_type = case_type
                elif result_type != case_type:
                    raise Exception(
                        "Erro Semântico: todos os casos do when têm de produzir o mesmo tipo"
                    )

            if result_type is None:
                raise Exception("Erro Semântico: o when tem de ter pelo menos um caso")

            return result_type

        if kind == "call":
            _, function_node, args = node
            function_name = self.resolve_function_name(function_node)

            if function_name not in self.signatures:
                raise Exception(
                    f"Erro Semântico: função '{function_name}' não tem assinatura declarada"
                )

            signature = self.signatures[function_name]
            expected_args = signature["args"]

            if len(args) != len(expected_args):
                raise Exception(
                    f"Erro Semântico: função '{function_name}' esperava {len(expected_args)} argumento(s), "
                    f"mas recebeu {len(args)}"
                )

            for index, (arg_node, expected_type) in enumerate(zip(args, expected_args), start=1):
                actual_type = self.infer_type(arg_node, local_types)
                if actual_type != expected_type:
                    raise Exception(
                        f"Erro Semântico: função '{function_name}' esperava argumento {index} do tipo "
                        f"{expected_type}, mas recebeu {actual_type}"
                    )

            return signature["return"]

        raise Exception(f"Erro Semântico: nó desconhecido '{kind}'")

    def eval(self, node):
        if type(node) in (int, bool):
            return node

        kind = node[0]

        if kind == "let":
            _, name, declared_type, value_expr = node

            if name in self.env_types or name in self.signatures or name in self.functions:
                raise Exception(f"Erro Semântico: identificador '{name}' já definido")

            actual_type = self.infer_type(value_expr)
            if declared_type != actual_type:
                raise Exception(
                    f"Erro Semântico: variável '{name}' declarada como {declared_type}, "
                    f"mas recebeu {actual_type}"
                )

            value = self.eval(value_expr)
            self.env[name] = value
            self.env_types[name] = declared_type
            return value

        if kind == "var":
            name = node[1]

            if name not in self.env:
                raise Exception(f"Erro: variável '{name}' não definida")

            return self.env[name]

        if kind == "fun_decl":
            _, name, arg_types, ret_type = node

            if name in self.env_types:
                raise Exception(f"Erro Semântico: identificador '{name}' já definido como variável")
            if name in self.signatures:
                raise Exception(f"Erro Semântico: assinatura da função '{name}' já definida")

            self.signatures[name] = {"args": arg_types, "return": ret_type}
            return None

        if kind == "fun_def":
            _, name, params, body = node

            if name not in self.signatures:
                raise Exception(f"Erro Semântico: função '{name}' não tem assinatura declarada")
            if name in self.functions:
                raise Exception(f"Erro Semântico: função '{name}' já definida")

            signature = self.signatures[name]
            expected_args = signature["args"]

            if len(params) != len(expected_args):
                raise Exception(
                    f"Erro Semântico: função '{name}' esperava {len(expected_args)} parâmetro(s), "
                    f"mas foram definidos {len(params)}"
                )

            if len(params) != len(set(params)):
                raise Exception(
                    f"Erro Semântico: a definição da função '{name}' tem parâmetros repetidos"
                )

            local_types = self.env_types.copy()
            for param_name, param_type in zip(params, expected_args):
                local_types[param_name] = param_type

            body_type = self.infer_type(body, local_types)
            if body_type != signature["return"]:
                raise Exception(
                    f"Erro Semântico: função '{name}' devia devolver {signature['return']}, "
                    f"mas devolve {body_type}"
                )

            self.functions[name] = {"params": params, "body": body}
            return None

        if kind == "call":
            _, function_node, args = node
            function_name = self.resolve_function_name(function_node)

            if function_name not in self.functions:
                raise Exception(f"Erro: função '{function_name}' não definida")

            signature = self.signatures.get(function_name)
            if signature is None:
                raise Exception(f"Erro: função '{function_name}' não tem assinatura declarada")

            expected_args = signature["args"]
            if len(args) != len(expected_args):
                raise Exception(
                    f"Erro: função '{function_name}' esperava {len(expected_args)} argumento(s), "
                    f"mas recebeu {len(args)}"
                )

            values = []
            for index, (arg_node, expected_type) in enumerate(zip(args, expected_args), start=1):
                value = self.eval(arg_node)
                actual_type = self.get_type(value)
                if actual_type != expected_type:
                    raise Exception(
                        f"Erro Semântico: função '{function_name}' esperava argumento {index} do tipo "
                        f"{expected_type}, mas recebeu {actual_type}"
                    )
                values.append(value)

            function = self.functions[function_name]
            if function_name in self.call_stack:
                raise Exception(
                    f"Erro Semântico: funções recursivas não são suportadas ('{function_name}')"
                )

            old_env = self.env.copy()
            old_env_types = self.env_types.copy()
            self.call_stack.append(function_name)

            try:
                for param_name, param_type, value in zip(function["params"], expected_args, values):
                    self.env[param_name] = value
                    self.env_types[param_name] = param_type

                result = self.eval(function["body"])
            finally:
                self.env = old_env
                self.env_types = old_env_types
                self.call_stack.pop()

            actual_ret_type = self.get_type(result)
            if actual_ret_type != signature["return"]:
                raise Exception(
                    f"Erro Semântico: função '{function_name}' devia devolver {signature['return']}, "
                    f"mas devolveu {actual_ret_type}"
                )

            return result

        if kind == "if":
            _, cond_node, then_node, else_node = node
            self.infer_type(node)

            cond_value = self.eval(cond_node)
            if type(cond_value) is not bool:
                raise Exception("Erro Semântico: a condição do if tem de ser Bool")

            return self.eval(then_node) if cond_value else self.eval(else_node)

        if kind == "when":
            _, subject_node, cases = node
            self.infer_type(node)

            subject_value = self.eval(subject_node)

            for _, patterns, expr in cases:
                has_wildcard = False
                for pattern in patterns:
                    if self.is_wildcard(pattern):
                        has_wildcard = True
                        continue
                    if subject_value == pattern:
                        return self.eval(expr)

                if has_wildcard:
                    return self.eval(expr)

            raise Exception("Erro Semântico: nenhum caso do when correspondeu ao valor analisado")

        if kind == "neg":
            _, expr = node
            value = self.eval(expr)
            if type(value) is not int:
                raise Exception("Erro Semântico: o operador unário '-' só pode ser usado com Int")
            return -value

        if kind == "binop":
            _, op, left_node, right_node = node
            left = self.eval(left_node)
            right = self.eval(right_node)
            left_type = self.get_type(left)
            right_type = self.get_type(right)

            if op in {"+", "-", "*", "/"}:
                if left_type != "Int" or right_type != "Int":
                    raise Exception(
                        "Erro Semântico: operações aritméticas só aceitam operandos do tipo Int"
                    )
                if op == "+":
                    return left + right
                if op == "-":
                    return left - right
                if op == "*":
                    return left * right
                if right == 0:
                    raise Exception("Erro: divisão por zero")
                return left // right

            if op in {"<", ">", ">=", "<="}:
                if left_type != "Int" or right_type != "Int":
                    raise Exception(
                        "Erro Semântico: comparações ordenadas só aceitam operandos do tipo Int"
                    )
                if op == "<":
                    return left < right
                if op == ">":
                    return left > right
                if op == ">=":
                    return left >= right
                return left <= right

            if op in {"==", "!="}:
                if left_type != right_type:
                    raise Exception(
                        "Erro Semântico: comparação entre valores de tipos incompatíveis"
                    )
                return left == right if op == "==" else left != right

        raise Exception(f"Erro: nó desconhecido '{kind}'")
