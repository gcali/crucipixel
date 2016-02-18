from typing import List


class CrucipixelScheme:

    def __init__(self,  title: str,
                        rows: List[List[int]],
                        cols: List[List[int]],
                        hard: int=0) -> None:
        self.title = title
        try:
            rows[0][0]
            cols[0][0]
        except IndexError:
            pass
        self.rows = rows
        self.cols = cols
        self.hard = hard

    def __str__(self) -> str:
        r = [
            self.title,
            "=" * len(self.title),
            "\tRows"
        ]
        for row in self.rows:
            r.append("\t\t" + str(row))
        r.append("\tCols")
        for col in self.cols:
            r.append("\t\t" + str(col))
        return "\n".join(r)


def main() -> int:
    print(CrucipixelScheme("Ciao", [[0]], [[1]]))

if __name__ == '__main__':
    main()
