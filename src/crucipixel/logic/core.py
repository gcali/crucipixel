'''
Created on Mar 13, 2015

@author: giovanni
'''
from itertools import zip_longest
from typing import Iterable

from crucipixel.data.complete_model import CrucipixelCompleteModel
from crucipixel.data.crucipixel_instance import MoveAtom, CrucipixelCellValue
from crucipixel.interface.puzzle_stage.guides import Orientation


class Crucipixel:

    def __init__(self, model: CrucipixelCompleteModel, index: int=0):

        self._model = model
        self.scheme = model.scheme
        if index >= len(model.instances):
            index = len(model.instances) - 1
        self.crucipixel_instance, self.guides_instance = model.instances[index]

    @property
    def number_of_rows(self) -> int:
        return len(self.scheme.rows)

    @property
    def number_of_cols(self) -> int:
        return len(self.scheme.cols)

    def make_move(self, atoms: Iterable[MoveAtom]):
        self.crucipixel_instance.make_move(atoms)

    def get_row_col_value(self, row: int, col: int) -> CrucipixelCellValue:
        return self.crucipixel_instance.get_row_col_value(row, col)

    def _get_line_iterator(self, orientation: Orientation,
                           line: int) -> Iterable[CrucipixelCellValue]:
        if orientation == Orientation.HORIZONTAL:
            return (self.get_row_col_value(line, i)
                    for i in range(len(self.scheme.cols)))
        else:
            return (self.get_row_col_value(i, line)
                    for i in range(len(self.scheme.rows)))

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
            else:
                return False

    def is_line_done(self, orientation: Orientation, line: int) -> bool:
        return not self.is_line_wrong(orientation, line)

    def is_line_full(self, orientation: Orientation, line: int) -> bool:
        for cell in self._get_line_iterator(orientation, line):
            if cell == CrucipixelCellValue.DEFAULT:
                return False
        else:
            return True

    def toggle_guide_cancelled(self, orientation: Orientation, line: int,
                               element: int):
        self.guides_instance.toggle_cancelled(orientation, line, element)


# class Crucipixel:
#
#     EMPTY=-1
#     DEFAULT=0
#     MAIN_SELECTED=1
#
#     @classmethod
#     def guides_from_strings(cls,
#                             rows:"int >0",
#                             cols:"int >0",
#                             row_guides:"string",
#                             col_guides:"string"):
#         row_guides = cls._guide_from_string(row_guides)
#         col_guides = cls._guide_from_string(col_guides)
#         return cls(rows=rows,
#                    cols=cols,
#                    row_guides=row_guides,
#                    col_guides=col_guides)
#
#     @classmethod
#     def guides_from_file(cls,
#                          file:"stream"):
#         lines = file.readlines()
#         rows = int(lines[0])
#         cols = int(lines[1])
#         row_guides_string = lines[2]
#         col_guides_string = lines[3]
#         return cls.guides_from_strings(rows, cols, row_guides_string, col_guides_string)
#
#     def __init__(self,rows:"int >0",cols:"int >0",
#                  row_guides:List[List[int]],
#                  col_guides:List[List[int]]):
#         self.rows = rows
#         self.cols = cols
#         self.row_guides = [list(row) for row in row_guides]
#         self.col_guides = [list(col) for col in col_guides]
#         self._matrix = [
#             [Crucipixel.DEFAULT for j in range(self.cols)]
#             for i in range(self.rows)
#         ]
#
#     @staticmethod
#     def check_line_done(line,guide):
#         pass
#
#     @staticmethod
#     def _create_minimal_line(line):
#         minimal_line = []
#         start_new = True
#         count = 0
#         for i in range(len(line)):
#             if line[i] != Crucipixel.EMPTY:
#                 count += 1
#                 start_new = False
#             elif not start_new:
#                 minimal_line.append(count)
#                 count = 0
#                 start_new = True
#
#         if count != 0:
#             minimal_line.append(count)
# #         if minimal_line:
# #             print(minimal_line)
#         return minimal_line
#
#     @staticmethod
#     def _check_line_not_wrong(line,guide):
#         for i in range(len(line)):
#             if line[i] == Crucipixel.DEFAULT:
#                 return True
#         minimal_line = Crucipixel._create_minimal_line(line)
# #         if minimal_line == [2,2]:
# #             print(guide)
#         for r,g in zip_longest(minimal_line,guide):
#             if r != g:
#                 return False
#         return True
#
#     def _get_row(self, row_id):
#         return self._matrix[row_id]
#
#     def _get_col(self, col_id):
#         return [self._matrix[i][col_id] for i in range(self.rows)]
#
#     def check_row_done(self, row_id):
#         row = self._get_row(row_id)
#         guide = self.row_guides[row_id]
#         for e in row:
#             if e == Crucipixel.DEFAULT:
#                 return False
#         return Crucipixel._check_line_not_wrong(row,guide)
#
#     def check_col_done(self,col_id):
#         col = self._get_col(col_id)
#         guide = self.col_guides[col_id]
#         for e in col:
#             if e == Crucipixel.DEFAULT:
#                 return False
#         return Crucipixel._check_line_not_wrong(col, guide)
#
#     def check_row_not_wrong(self,row_id):
#         row = self._get_row(row_id)
#         guide = self.row_guides[row_id]
#         return Crucipixel._check_line_not_wrong(row,guide)
#
#     def check_col_not_wrong(self,col_id):
#         col = self._get_col(col_id)
#         guide = self.col_guides[col_id]
#         return Crucipixel._check_line_not_wrong(col, guide)
#
#     def check_ok(self):
#         for row_id in range(self.rows):
#             if not self.check_row_not_wrong(row_id):
#                 return False
#         for col_id in range(self.cols):
#             if not self.check_col_not_wrong(col_id):
#                 return False
#         return True
#
#     def update(self, cell_to_update: Tuple[int, int, int]):
#         for (row, col, status) in cell_to_update:
#             print("Update!", row, col, status)
#             self[row, col] = status
#         results_rows = []
#         results_cols = []
#         for row_id in range(self.rows):
#             if not self.check_row_not_wrong(row_id):
#                 results_rows.append(("wrong", row_id))
#             elif self.check_row_done(row_id):
#                 results_rows.append(("done", row_id))
#         for col_id in range(self.cols):
#             if not self.check_col_not_wrong(col_id):
#                 results_cols.append(("wrong", col_id))
#             elif self.check_col_done(col_id):
#                 results_cols.append(("done", col_id))
#         return results_rows, results_cols
#
#     @staticmethod
#     def _guide_from_string(string) -> "guide":
#         """ Format: ',' separates elements of the same section,
#                     ';' separates sections
#         """
#         string = ''.join(string.split())
#         sections = string.split(";")
#         return [ [int(e) for e in s.split(",")] for s in sections if s != ""]
#
#     @staticmethod
#     def _guide_to_string(guide:"guide") -> "string":
#         return ";".join([",".join([str(e) for e in section]) for section in guide])
#
#     def __getitem__(self,key):
#         i,j = key
#         return self._matrix[i][j]
#
#     def __setitem__(self,key,value):
#         i,j = key
#         print("set", i, j)
#         self._matrix[i][j] = value
#
#     def __str__(self):
#         rows_str = [" ".join([str(self[i,j]).rjust(2) for j in range(self.cols)])\
#                 for i in range(self.rows)]
#         row_guides = "Row guides: " + Crucipixel._guide_to_string(self.row_guides)
#         col_guides = "Col guides: " + Crucipixel._guide_to_string(self.col_guides)
#         total_str = rows_str + [row_guides] + [col_guides]
#         return "\n".join(total_str)
#
#
# def scheme_to_core(scheme: CrucipixelScheme) -> Crucipixel:
#     return Crucipixel(
#         len(scheme.rows),
#         len(scheme.cols),
#         scheme.rows,
#         scheme.cols
#     )
