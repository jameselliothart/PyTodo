import os
from typing import List


def write_all_lines(path: str, lines: List[str]):
    with open(path, 'w') as f:
        for line in lines:
            print(line, file=f)

def append_line(path: str, line: str):
    with open(path, 'a') as f:
        print(line, file=f)

def read_all_lines(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [line.strip() for line in f.readlines()]
