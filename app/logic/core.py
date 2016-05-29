'''
Created on Mar 13, 2015

@author: giovanni
'''
import random
from itertools import zip_longest
from typing import Iterable, Tuple, List

from app.data.complete_model import CrucipixelCompleteModel
from app.data.crucipixel_instance import MoveAtom, CrucipixelCellValue, \
    CrucipixelInstance
from app.data.crucipixel_scheme import CrucipixelScheme
from app.data.guides_instance import GuidesInstance
from app.data.json_parser import parse_file_name
from app.data.storage import save_model, get_default_path_from_title
from app.interface.puzzle_stage.guides import Orientation


class Crucipixel:

    def __init__(self, model: CrucipixelCompleteModel, index: int=0):

        self._model = model
        self.scheme = model.scheme
        if index >= len(model.instances):
            index = len(model.instances) - 1
        self.index = index
        self.crucipixel_instance, self.guides_instance = model.instances[index]

        self.on_won_change_callbacks_list = []

        self._is_won = False
        self._check_if_won()

    @property
    def number_of_rows(self) -> int:
        return len(self.scheme.rows)

    @property
    def number_of_cols(self) -> int:
        return len(self.scheme.cols)

    def make_move(self, atoms: Iterable[MoveAtom]):
        """
        Commits a unit of moves to the instance of the app

        Args:
            atoms: a sequence of moves, interpreted as a single unit
        """
        self.crucipixel_instance.make_move(atoms)
        self._check_if_won()

    def undo_move(self) -> Iterable[MoveAtom]:
        undo = self.crucipixel_instance.undo_last_move()
        self._check_if_won()
        return undo

    def get_row_col_value(self, row: int, col: int) -> CrucipixelCellValue:
        return self.crucipixel_instance.get_row_col_value(row, col)

    def _get_line_iterator(self, orientation: Orientation,
                           line: int) -> Iterable[CrucipixelCellValue]:
        if orientation == Orientation.HORIZONTAL:
            return (self.get_row_col_value(line, i)
                    for i in range(self.number_of_cols))
        else:
            return (self.get_row_col_value(i, line)
                    for i in range(self.number_of_rows))

    def _get_minimal_line_iterator(self, orientation: Orientation,
                                   line: int) -> Iterable[CrucipixelCellValue]:
        found_empty = True
        for cell in self._get_line_iterator(orientation, line):
            if cell != CrucipixelCellValue.EMPTY:
                found_empty = False
                yield cell
            elif not found_empty:
                found_empty = True
                yield cell

    @staticmethod
    def _get_guide_from_minimal_line(line: Iterable[CrucipixelCellValue]) \
            -> Iterable[int]:
        current = 0
        for element in line:
            if element == CrucipixelCellValue.EMPTY and current > 0:
                yield current
                current = 0
            elif element == CrucipixelCellValue.SELECTED:
                current += 1
        if current != 0:
            yield current

    def _get_rows_cols_guides(self) -> Tuple[List[List[int]], List[List[int]]]:
        rows = [
            list(CrucipixelEditor._get_guide_from_minimal_line(
                self._get_minimal_line_iterator(Orientation.HORIZONTAL, line)
            ))
            for line in range(self.number_of_rows)
            ]
        cols = [
            list(CrucipixelEditor._get_guide_from_minimal_line(
                self._get_minimal_line_iterator(Orientation.VERTICAL, line)
            ))
            for line in range(self.number_of_cols)
            ]

        return rows, cols

    def is_line_wrong(self, orientation: Orientation, line: int) -> bool:
        if orientation == Orientation.HORIZONTAL:
            guide = self.scheme.rows[line]
        else:
            guide = self.scheme.cols[line]

        guide_from_line = Crucipixel._get_guide_from_minimal_line(
            self._get_minimal_line_iterator(orientation, line)
        )

        for original, custom in zip_longest(guide, guide_from_line):
            if original != custom:
                return True
        return False

    def is_line_done(self, orientation: Orientation, line: int) -> bool:
        return not self.is_line_wrong(orientation, line)

    def is_line_full(self, orientation: Orientation, line: int) -> bool:
        for cell in self._get_line_iterator(orientation, line):
            if cell == CrucipixelCellValue.DEFAULT:
                return False
        else:
            return True

    @property
    def is_won(self) -> bool:
        return self._is_won

    @is_won.setter
    def is_won(self, value: bool):
        old_value = self._is_won
        self._is_won = value
        if value != old_value:
            self.on_won_change_callbacks_list = [
                callback for callback in self.on_won_change_callbacks_list
                if not callback(value)
            ]
            # for callback in self.on_won_change_callbacks_list:
            #     callback(value)

    def _check_if_won(self):
        for line in range(self.number_of_rows):
            if (not self.is_line_full(Orientation.HORIZONTAL, line)) or\
                    self.is_line_wrong(Orientation.HORIZONTAL, line):
                self.is_won = False
                return
        for col in range(self.number_of_cols):
            if (not self.is_line_full(Orientation.VERTICAL, col)) or \
                    self.is_line_wrong(Orientation.VERTICAL, col):
                self.is_won = False
                return

        self.is_won = True

    def toggle_guide_cancelled(self, orientation: Orientation, line: int,
                               element: int):
        self.guides_instance.toggle_cancelled(orientation, line, element)

    def save(self):
        save_model(self._model)

    def load(self):
        self.__init__(parse_file_name(self._model.file_name_complete))


class CrucipixelEditor(Crucipixel):

    def __init__(self, rows: int, cols: int, hard: int, title: str):

        # super().__init__()
        self.__number_of_rows = rows
        self.__number_of_cols = cols
        self.hard = hard
        self.title = title
        self.crucipixel_instance = CrucipixelInstance(rows, cols)

        self.on_won_change_callbacks_list = []

        self._is_won = False

        self._check_if_won()

    @property
    def number_of_rows(self) -> int:
        return self.__number_of_rows

    @property
    def number_of_cols(self) -> int:
        return self.__number_of_cols

    def is_line_wrong(self, orientation: Orientation, line: int) -> bool:
        return False

    def is_line_done(self, orientation: Orientation, line: int) -> bool:
        return self.is_line_full(orientation, line)

    def toggle_guide_cancelled(self, orientation: Orientation, line: int,
                               element: int):
        pass

    def save(self, force=False) -> None:
        """

        Args:
            force: if True, overwrites data if a scheme with the same name
                   exists; if False, in case of collision raises FileExistsError

        Raises:
            FileExistsError: a scheme with the same name already exists
                             and force was False

        """
        file_name = get_default_path_from_title(self.title)
        if not force:
            with open(file_name, 'x'):
                pass
        rows, cols = self._get_rows_cols_guides()
        scheme = CrucipixelScheme(self.title, rows, cols, self.hard)
        model = CrucipixelCompleteModel(scheme, [])
        model.file_name_complete = file_name
        save_model(model)

    def load(self):
        self.__init__(parse_file_name(self._model.file_name_complete))

def main():
    editor = CrucipixelEditor(10, 10, "ciao")

    move = []
    for row in range(10):
        for col in range(10):
            if random.randint(0, 1) == 0:
                value = CrucipixelCellValue.EMPTY
            else:
                value = CrucipixelCellValue.SELECTED
            move.append(MoveAtom(row, col, value))

    editor.make_move(move)

    editor.save()

if __name__ == '__main__':
    main()
