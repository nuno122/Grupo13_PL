import sys
from pathlib import Path

from interpreter import Interpreter
from parser import MiniFunParser


def load_input() -> str | None:
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        return path.read_text(encoding="utf-8")
    return None


def run_source(source: str, parser: MiniFunParser, interpreter: Interpreter):
    ast = parser.parse(source)
    if not ast:
        return

    for expr in ast:
        result = interpreter.eval(expr)
        if result is not None:
            print(result)


def main():
    parser = MiniFunParser()
    interpreter = Interpreter()

    try:
        source = load_input()

        if source is not None:
            run_source(source, parser, interpreter)
            return

        print("Modo interativo (Ctrl+C para sair)")
        while True:
            line = input(">> ")
            run_source(line, parser, interpreter)

    except KeyboardInterrupt:
        print("\nA terminar.")
    except FileNotFoundError as exc:
        print(f"Erro: ficheiro não encontrado ({exc.filename})")
    except Exception as exc:
        print(exc)


if __name__ == "__main__":
    main()
