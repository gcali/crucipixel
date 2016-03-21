import io
from json.encoder import JSONEncoder
from typing import List, IO
import json

from crucipixel.data.crucipixel_scheme import CrucipixelScheme

class MyEncoder(JSONEncoder):

    def default(self, o):
        try:
            return o.to_json_object()
        except AttributeError:
            return super().default(o)


def encode_scheme(scheme: CrucipixelScheme) -> str:
    return json.dumps(scheme, cls=MyEncoder, indent=4)


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
    # for name in files:
    #     scheme = parse_file_name("../data/" + name)
    #     print(scheme)
    name = files[0]

    scheme = parse_file_name("../data/" + name)
    print(scheme)
    print(parse_string(encode_scheme(scheme)))
