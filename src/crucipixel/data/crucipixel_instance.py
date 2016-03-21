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
        self.value = value.value

    def to_json_object(self) -> object:
        return [
            self.row,
            self.col,
            self.value
        ]

    @staticmethod
    def from_json_object(o: object) -> "MoveAtom":
        return MoveAtom(o[0], o[1], CrucipixelCellValue(o[2]))

    def __str__(self):
        return "({},{}|{})".format(self.row, self.col, self.value)


Move = list


class CrucipixelInstance:

    def __init__(self, rows: int, cols: int,
                 status: List[List[CrucipixelCellValue]] = None,
                 moves: List[Move] = None):

        self.rows = rows
        self.cols = cols

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

    def to_json_object(self) -> object:
        return {
            'rows': self.rows,
            'cols': self.cols,
            'status': [
                [self.status[row][col] for col in range(self.cols)]
                for row in range(self.rows)
            ],
            'moves': [
                [atom.to_json_object() for atom in move]
                for move in self.moves
            ]
        }

    @staticmethod
    def from_json_object(o: object) -> "CrucipixelInstance":
        moves = [
            [MoveAtom.from_json_object(atom_json) for atom_json in move]
            for move in o['moves']
        ]
        status = o['status']
        rows = o['rows']
        cols = o['cols']

        return CrucipixelInstance(rows, cols, status, moves)

    def get_row_col_value(self, row: int, col: int) -> CrucipixelCellValue:
        return self.status[row][col]

    def make_move(self, atoms: Iterable[MoveAtom]):
        move = []
        for atom in atoms:
            # atom._back_value = self.status[atom.row][atom.col]
            move.append(MoveAtom(
                atom.row, atom.col, self.status[atom.row][atom.col]
            ))
            self.status[atom.row][atom.col] = atom.value
        self.moves.append(move)

    def undo_last_move(self):
        last_move = self.moves.pop()
        for atom in reversed(last_move):
            self.status[atom.row][atom.col] = atom.value

    def __str__(self):
        return str(self.status)


def main():
    instance = CrucipixelInstance(2,2)

    instance.make_move([MoveAtom(0, 0, CrucipixelCellValue.SELECTED)])
    print(instance.to_json_object())
    instance.undo_last_move()
    print(instance.to_json_object())

    instance.make_move([MoveAtom(0, 0, CrucipixelCellValue.SELECTED),
                        MoveAtom(0, 1, CrucipixelCellValue.SELECTED)])
    print("Start:")
    print(instance.rows, instance.cols)
    print(instance)
    print([",".join(str(a) for a in m) for m in instance.moves])

    test_object = instance.to_json_object()
    instance = CrucipixelInstance.from_json_object(test_object)

    print("Result:")
    print(instance.rows, instance.cols)
    print(instance)
    print([",".join(str(a) for a in m) for m in instance.moves])


if __name__ == '__main__':
    main()

