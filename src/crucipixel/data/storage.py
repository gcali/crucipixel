import os, glob
from typing import List

from crucipixel.data import json_parser
from crucipixel.data.crucipixel_scheme import CrucipixelScheme
from crucipixel.options import Options


def assure_path(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def _get_default_schemes_path() -> str:
    try:
        return os.environ['PCRUCIPIXEL_PATH']
    except KeyError:
        try:
            return os.environ['HOME'] + os.sep + ".crucipixel"
        except KeyError:
            return os.getcwd()


def get_schemes(options: Options = None) -> List[CrucipixelScheme]:
    if options is None or options.schemes_path is None:
        path = _get_default_schemes_path()
    else:
        path = options.schemes_path

    assure_path(path)
    file_names = [name for name in glob.iglob(path + os.sep + "*.json")]

    return [json_parser.parse_file_name(name).scheme for name in file_names]


def main() -> int:

    for scheme in get_schemes():
        print(scheme)


if __name__ == '__main__':
    main()
