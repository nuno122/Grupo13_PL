import sys
import re
from pathlib import Path

from interpreter import Interpreter
from parser import MiniFunParser


def load_input() -> str | None:
    # Le um ficheiro .lf.
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        return path.read_text(encoding="utf-8")
    return None


def format_value(value):
    if type(value) is bool:
        return "true" if value else "false"
    return str(value)


def format_result(value, interpreter: Interpreter) -> str:
    return f"resultado: {format_value(value)} tipo: {interpreter.get_type(value)}"


def run_source(source: str, parser: MiniFunParser, interpreter: Interpreter):
    # Faz parsing do codigo e executa cada instrucao pela ordem original.
    ast = parser.parse(source)
    if not ast:
        return

    for expr in ast:
        result = interpreter.eval(expr)
        if result is not None:
            print(format_result(result, interpreter))


def is_block_complete(source: str) -> bool:
    # Ignora comentarios antes de verificar se um bloco interativo terminou.
    cleaned = re.sub(r"\{-[\s\S]*?-\}", "", source)
    cleaned = re.sub(r"--[^\n]*", "", cleaned)
    stripped = cleaned.strip()
    if not stripped:
        return False

    if not stripped.endswith(";"):
        return False

    when_count = stripped.count("when")
    end_count = stripped.count("end")
    return when_count == end_count


def interactive_mode(parser: MiniFunParser, interpreter: Interpreter):
    # Permite introduzir instrucoes diretamente no terminal.
    print("Modo interativo (Ctrl+C para sair)")
    buffer = []

    while True:
        prompt = ">> " if not buffer else ".. "
        line = input(prompt)

        if not line.strip() and not buffer:
            continue

        buffer.append(line)
        source = "\n".join(buffer)

        if not is_block_complete(source):
            continue

        run_source(source, parser, interpreter)
        buffer.clear()


def main():
    parser = MiniFunParser()
    interpreter = Interpreter()

    try:
        source = load_input()

        if source is not None:
            run_source(source, parser, interpreter)
            return

        interactive_mode(parser, interpreter)

    except KeyboardInterrupt:
        print("\nA terminar.")
    except EOFError:
        print("\nA terminar.")
    except FileNotFoundError as exc:
        print(f"Erro: ficheiro nao encontrado ({exc.filename})")
    except Exception as exc:
        print(exc)


if __name__ == "__main__":
    main()
