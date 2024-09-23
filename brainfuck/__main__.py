import argparse
from dataclasses import dataclass

from brainfuck.compiler import compile


@dataclass
class CliArgs:
    filename: str


def parse_cli_args() -> CliArgs:
    parser = argparse.ArgumentParser(description="Brainfuck compiler")
    parser.add_argument("filename", help="Input source code")
    args = parser.parse_args()

    return CliArgs(filename=args.filename)


def main() -> None:
    args = parse_cli_args()
    compile(args.filename)


if __name__ == "__main__":
    # Do not put any other code here, as poetry's `brainfuck` entrypoint
    # executes the `main` function directly (i.e. anything out of `main` will
    # not be executed if running with `$ poetry run brainfuck`).
    main()
