from pathlib import Path
import random
import subprocess

# This limits how much memory the brainfuck program will have.
NUM_CELLS = 300_000

# Each pair of square brackets becomes a pair of labels. This parameter
# limits what the maximum number of labels is. If the program requires
# more labels than this, the compiler will get stuck in an infinite loop
# attempting to find a unique label.
MAX_LABELS = NUM_CELLS * 10


def compile(filename: str) -> None:
    with open(filename, "r") as f:
        content = f.read()

    input_filename_without_ext = Path(filename).stem
    c_file = f"{input_filename_without_ext}.c"

    c_to_out_command = (
        f"gcc -Wall -Wextra -Wpedantic -Werror -O3 {c_file} -fsanitize=undefined "
        f"-o {input_filename_without_ext}"
    )

    # Step 1: brainfuck-to-C compilation
    labels_stack: list[int] = []
    used_labels = set()

    def make_unique_label_id() -> int:
        while (c := random.randint(0, MAX_LABELS)) in used_labels:
            pass
        return c

    w = OutputWriter(output_filename=c_file)
    w.add_line(f"// This will be compiled to machine code with: {c_to_out_command}")
    w.add_line("#include <stdio.h>\n")
    w.add_line("int input;")
    w.add_line(f"int cells[{NUM_CELLS}] = {{0}};")
    w.add_line("int main() {")
    w.indent()
    w.add_line("int* data_ptr = cells;")
    for c in content:
        match c:
            case ">":
                w.add_line("++data_ptr;")
            case "<":
                w.add_line("--data_ptr;")
            case "+":
                w.add_line("++(*data_ptr);")
            case "-":
                w.add_line("--(*data_ptr);")
            case ".":
                w.add_line('printf("%c", (char)*data_ptr);')
                w.add_line("fflush(stdout);")
            case ",":
                w.add_line("input = fgetc(stdin);")
                w.add_line("if (input != EOF) (*data_ptr) = input;")
            case "[":
                new_label = make_unique_label_id()
                labels_stack.append(new_label)
                used_labels.add(new_label)

                w.dedent()
                w.add_line(f"l{new_label}b:")
                w.indent()
                w.add_line(f"if ((*data_ptr) == 0) goto l{new_label}f;")
            case "]":
                # SAFETY: This should never IndexError - unless the square brackets aren't balanced.
                matching_label = labels_stack[-1]
                w.dedent()
                w.add_line(f"l{matching_label}f:")
                w.indent()
                w.add_line(f"if ((*data_ptr) != 0) goto l{matching_label}b;")
                labels_stack.pop()
                pass
            case _:
                pass
    w.dedent()
    w.add_line("}")
    w.write_output_file()

    # Step 2: C-to-machine compilation
    subprocess.run(c_to_out_command.split(), check=True)


class OutputWriter:
    _output_filename: str
    _content: str = ""
    _indentation_level = 0

    def __init__(self, *, output_filename: str):
        self._output_filename = output_filename

    def add_line(self, line: str):
        indentation = self._indentation_level * " "
        self._content += f"{indentation}{line}\n"

    def indent(self):
        self._indentation_level += 4

    def dedent(self):
        self._indentation_level -= 4

    def write_output_file(self):
        with open(self._output_filename, "w") as f:
            f.write(self._content)
