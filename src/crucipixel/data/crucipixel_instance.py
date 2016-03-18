from enum import Enum
from typing import List, Iterable


class CrucipixelCellValue(Enum):

    DEFAULT = 0
    EMPTY = 1
    SELECTED = 2


class MoveAtom:

    def __init__(self, row: int, col: int, value: CrucipixelCellValue):
        self.row = row
        self.col = col
        self.forward_value = value
        self._back_value = None


Move = list


class CrucipixelInstance:

    def __init__(self, rows: int, cols: int,
                 status: List[List[CrucipixelCellValue]] = None,
                 moves: List[Move] = None):

        self.rows = rows
        self.cols = cols

        self.horizontal_cancelled = []
        self.vertical_cancelled = []

        if status is None:
            self.status = [
                [CrucipixelCellValue.DEFAULT for _ in range(cols)]
                for _ in range(rows)
            ]
        else:
            self.status = status

        if moves is None:
            self.moves = []
        else:
            self.moves = moves

    def get_row_col_value(self, row: int, col: int) -> CrucipixelCellValue:
        return self.status[row][col]

    def make_move(self, atoms: Iterable[MoveAtom]):
        move = []
        for atom in atoms:
            atom._back_value = self.status[atom.row][atom.col]
            self.status[atom.row][atom.col] = atom.forward_value
            move.append(atom)
        self.moves.append(move)

    def undo_last_move(self):
        last_move = self.moves.pop()
        for atom in reversed(last_move):
            self.status[atom.row][atom.col] = atom._back_value

    def __str__(self):
        return str(self.status)


def main():
    instance = CrucipixelInstance(2,2)

    instance.make_move([MoveAtom(0, 0, CrucipixelCellValue.SELECTED)])
    print(instance)
    instance.undo_last_move()
    print(instance)


if __name__ == '__main__':
    main()

