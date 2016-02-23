import io
from typing import List, IO
import json

from crucipixel.data.crucipixel_scheme import CrucipixelScheme


def encode_scheme(scheme: CrucipixelScheme) -> str:
    title = scheme.title
    rows = scheme.rows
    cols = scheme.cols

    json_object = {
        "title": title,
        "rows": rows,
        "cols": cols
    }
    try:
        hard = scheme.hard
        if hard is not None and hard > 0:
            json_object["hard"] = hard
    except AttributeError:
        pass

    return json.dumps(json_object, indent=4)


def parse_string(s: str) -> CrucipixelScheme:
    return parse_file(io.StringIO(s))


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
    files=["al_parco.json", "brachiosauri.json", "monopattino.json", "mostro.json"]
    for name in files:
        scheme = parse_file_name("../data/" + name)
        new_cols = [list(reversed(l)) for l in scheme.cols]
        print(new_cols)
        scheme.cols = new_cols
        new_string = encode_scheme(scheme)
        with open("../data/" + name, "w") as f:
            print(new_string, file=f)
