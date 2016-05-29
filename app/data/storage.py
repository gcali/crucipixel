import os, glob, re
from typing import List

from app.data import json_parser
from app.data.complete_model import CrucipixelCompleteModel
from app.data.crucipixel_scheme import CrucipixelScheme
from app.data.json_parser import encode_model
from app.options import Options



class UnknownPathException(Exception):
    pass


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


def get_default_path_from_title(title: str) -> str:
    default_schemes_path = _get_default_schemes_path()
    title_converted = re.sub('\s+', '_', title).strip().lower()
    return default_schemes_path + os.sep + title_converted + ".json"


def get_models(options: Options = None) -> List[CrucipixelCompleteModel]:
    if options is None or options.schemes_path is None:
        path = _get_default_schemes_path()
    else:
        path = options.schemes_path

    assure_path(path)
    file_names = [name for name in glob.iglob(path + os.sep + "*.json")]

    return [json_parser.parse_file_name(name) for name in file_names]


def save_model(model: CrucipixelCompleteModel, path: str = None):
    if path is None:
        if model.file_name_complete is None:
            raise UnknownPathException
        else:
            path = model.file_name_complete

    with open(path, "w") as f:
        print(encode_model(model), file=f)


def main() -> int:

    print(get_default_path_from_title("Ciao io sono uno schema     !!!\t ciao"))


if __name__ == '__main__':
    main()
