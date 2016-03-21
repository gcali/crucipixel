from time import sleep
from typing import Iterable, Tuple

from crucipixel.interface.puzzle_stage.guides import Orientation


class GuidesInstance:

    def __init__(self, cancelled: Iterable[Tuple[Orientation, int, int]] = None):

        if cancelled is None:
            self._cancelled = set()
        else:
            self._cancelled = set(cancelled)

    def is_cancelled(self, orientation: Orientation, line: int,
                     element: int) -> bool:
        return (orientation, line, element) in self._cancelled

    def set_cancelled(self, orientation: Orientation, line: int, element: int,
                      value: bool):
        self._cancelled.add((orientation, line, element))

    def toggle_cancelled(self, orientation: Orientation, line: int,
                         element: int):
        t = orientation, line, element
        if t in self._cancelled:
            self._cancelled.remove(t)
        else:
            self._cancelled.add(t)

    def iter_over_orientation(self, orientation: Orientation) \
            -> Iterable[Tuple[int, int]]:
        for k in self:
            if k[0] == orientation:
                yield k[1], k[2]

    def __iter__(self):
        return self._cancelled.__iter__()

    def to_json_object(self) -> object:
        return [[value.value, row, col] for (value, row, col) in self]

    @staticmethod
    def from_json_object(json_object: object) -> "GuidesInstance":
        return GuidesInstance(((Orientation(value), row, col) for value, row, col in json_object))


def main():
    guide_instance = GuidesInstance()

    guide_instance.toggle_cancelled(Orientation.HORIZONTAL, 0, 0)
    print("Before")
    for e in guide_instance:
        print(e)
    guide_instance.toggle_cancelled(Orientation.HORIZONTAL, 0, 0)
    print("After")
    for e in guide_instance:
        print(e)

    guide_instance.toggle_cancelled(Orientation.HORIZONTAL, 0, 1)
    guide_instance.toggle_cancelled(Orientation.HORIZONTAL, 2, 1)
    guide_instance.toggle_cancelled(Orientation.VERTICAL, 3, 1)
    guide_instance.toggle_cancelled(Orientation.VERTICAL, 2, 1)
    print("-" * 8)
    for e in guide_instance.iter_over_orientation(Orientation.HORIZONTAL):
        print(e)
    print("-" * 8)
    for e in guide_instance.iter_over_orientation(Orientation.VERTICAL):
        print(e)

    print("-" * 8)
    for e in GuidesInstance.from_json_object(guide_instance.to_json_object()):
        print(e)

if __name__ == '__main__':
    main()