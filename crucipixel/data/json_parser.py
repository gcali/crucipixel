import io
import os
from enum import Enum
from json.encoder import JSONEncoder
from time import sleep
from typing import List, IO, Tuple
import json

from crucipixel.data.complete_model import CrucipixelCompleteModel
from crucipixel.data.crucipixel_instance import CrucipixelInstance
from crucipixel.data.crucipixel_scheme import CrucipixelScheme
from crucipixel.data.guides_instance import GuidesInstance
from crucipixel.interface.puzzle_stage.guides import Orientation


class MyEncoder(JSONEncoder):

    def default(self, o):
        try:
            if isinstance(o, Enum):
                return o.value
            return o.to_json_object()
        except AttributeError:
            return super().default(o)


def encode_model(model: CrucipixelCompleteModel) -> str:
    return json.dumps(model, cls=MyEncoder, indent=4)


def parse_file(f: IO) -> CrucipixelCompleteModel:
    loaded = json.load(f)
    return CrucipixelCompleteModel.from_json_object(loaded)


# def encode_scheme(scheme: CrucipixelScheme) -> str:
#     return json.dumps(scheme, cls=MyEncoder, indent=4)


def parse_string(s: str) -> CrucipixelCompleteModel:
    return parse_file(io.StringIO(s))


# def parse_file(f: IO) -> CrucipixelScheme:
#     loaded_json = json.load(f)
#     title = loaded_json['title']
#     rows = loaded_json['rows']
#     cols = loaded_json['cols']
#     try:
#         hard = loaded_json['hard']
#     except KeyError:
#         hard = 0
#     return CrucipixelScheme(title, rows, cols, hard)


def parse_file_name(file_name: str) -> CrucipixelCompleteModel:
    with open(file_name, 'r') as f:
        parsed = parse_file(f)
        parsed.file_name_complete = file_name
        return parsed

