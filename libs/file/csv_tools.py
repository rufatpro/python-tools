import csv
from typing import List


def load_csv(filename, encoding="utf-8", delimiter=";"):
    with open(filename, "r", encoding=encoding) as file_reader:
        return list(csv.reader(file_reader, delimiter=delimiter))


def load_not_empty_lines(filename, encoding="utf-8"):
    lines: List[str] = []
    with open(filename, "r", encoding=encoding) as file_reader:
        for line in file_reader:
            line_mod = line.strip()
            if line_mod != "":
                lines.append(line_mod)
    return lines
