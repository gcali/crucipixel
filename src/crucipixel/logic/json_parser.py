from typing import List, IO
import json

from crucipixel.data.crucipixel_scheme import CrucipixelScheme


def parse_file(f: IO) -> CrucipixelScheme:
    loaded_json = json.load(f)
    title = loaded_json['title']
    rows = loaded_json['rows']
    cols = loaded_json['cols']
    try:
        hard = loaded_json['hard']
    except KeyError:
        hard = 0
    return CrucipixelScheme(title, rows, cols, hard)


def parse_file_name(file_name: str) -> CrucipixelScheme:
    with open(file_name, 'r') as f:
        return parse_file(f)


def main(args: List[str]) -> int:
    for s in args:
        print(parse_file_name(s))


if __name__ == '__main__':
    from sys import argv
    main(argv[1:])