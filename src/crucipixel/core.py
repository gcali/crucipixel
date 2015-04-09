'''
Created on Mar 13, 2015

@author: giovanni
'''
from itertools import zip_longest
from sys import argv

class Crucipixel:
    
    EMPTY=-1
    DEFAULT=0
    MAIN_SELECTED=1
    
    @classmethod
    def guides_from_strings(cls,
                            rows:"int >0",
                            cols:"int >0",
                            row_guides:"string",
                            col_guides:"string"):
        row_guides = cls._guide_from_string(row_guides)
        col_guides = cls._guide_from_string(col_guides)
        return cls(rows=rows,
                   cols=cols,
                   row_guides=row_guides,
                   col_guides=col_guides)
    
    @classmethod
    def guides_from_file(cls,
                         file:"stream"):
        lines = file.readlines()
        rows = int(lines[0])
        cols = int(lines[1])
        row_guides_string = lines[2]
        col_guides_string = lines[3]
        return cls.guides_from_strings(rows, cols, row_guides_string, col_guides_string)

    def __init__(self,rows:"int >0",cols:"int >0",
                 row_guides:"iter of iter of int >0",
                 col_guides:"iter of iter of int >0"):
        self.rows = rows
        self.cols = cols
        self.row_guides = [list(row) for row in row_guides]
        self.col_guides = [list(col) for col in col_guides]
        self._matrix = [[Crucipixel.DEFAULT for j in range(self.cols)] for i in range(self.rows)]  # @UnusedVariable 
        
    @staticmethod
    def check_line_done(line,guide):
        pass
    
    @staticmethod 
    def _create_minimal_line(line):
        minimal_line = []
        start_new = True
        count = 0
        for i in range(len(line)):
            if line[i] != Crucipixel.EMPTY:
                count += 1
                start_new = False
            elif not start_new:
                minimal_line.append(count)
                count = 0
                start_new = True
        
        if count != 0:
            minimal_line.append(count)
#         if minimal_line:
#             print(minimal_line)
        return minimal_line

    @staticmethod
    def _check_line_not_wrong(line,guide):
        for i in range(len(line)):
            if line[i] == Crucipixel.DEFAULT:
                return True
        minimal_line = Crucipixel._create_minimal_line(line)
#         if minimal_line == [2,2]:
#             print(guide)
        for r,g in zip_longest(minimal_line,guide):
            if r != g:
                return False
        return True 
    
    def _get_row(self,row_id):
        return self._matrix[row_id] 
    
    def _get_col(self,col_id):
        return [self._matrix[i][col_id] for i in range(self.rows)]
    
    def check_row_done(self,row_id):
        row = self._get_row(row_id)
        guide = self.row_guides[row_id]
        for e in row:
            if e == Crucipixel.DEFAULT:
                return False
        return Crucipixel._check_line_not_wrong(row,guide)
    
    def check_col_done(self,col_id):
        col = self._get_col(col_id)
        guide = self.col_guides[col_id]
        for e in col:
            if e == Crucipixel.DEFAULT:
                return False
        return Crucipixel._check_line_not_wrong(col, guide)
    
    def check_row_not_wrong(self,row_id):
        row = self._get_row(row_id)
        guide = self.row_guides[row_id]
        return Crucipixel._check_line_not_wrong(row,guide)
    
    def check_col_not_wrong(self,col_id):
        col = self._get_col(col_id)
        guide = self.col_guides[col_id]
        return Crucipixel._check_line_not_wrong(col, guide)
    
    def check_ok(self): 
        for row_id in range(self.rows):
            if not self.check_row_not_wrong(row_id):
                return False
        for col_id in range(self.cols):
            if not self.check_col_not_wrong(col_id):
                return False
        return True
    
    def update(self,cell_to_update:"iter"):
        for (row,col,status) in cell_to_update:
            self[row,col] = status
        results_rows = []
        results_cols = []
        for row_id in range(self.rows):
            if not self.check_row_not_wrong(row_id):
                results_rows.append(("wrong",row_id))
            elif self.check_row_done(row_id):
                results_rows.append(("done",row_id))
        for col_id in range(self.cols):
            if not self.check_col_not_wrong(col_id):
                results_cols.append(("wrong",col_id))
            elif self.check_col_done(col_id):
                results_cols.append(("done",col_id))
        return (results_rows,results_cols)
    
    @staticmethod
    def _guide_from_string(string) -> "guide":
        """ Format: ',' separates elements of the same section,
                    ';' separates sections
        """
        string = ''.join(string.split())
        sections = string.split(";") 
        return [ [int(e) for e in s.split(",")] for s in sections if s != ""]
    
    @staticmethod
    def _guide_to_string(guide:"guide") -> "string":
        return ";".join([",".join([str(e) for e in section]) for section in guide])

    def __getitem__(self,key):
        i,j = key
        return self._matrix[i][j]
    
    def __setitem__(self,key,value):
        i,j = key
        self._matrix[i][j] = value
    
    def __str__(self):
        rows_str = [" ".join([str(self[i,j]).rjust(2) for j in range(self.cols)])\
                for i in range(self.rows)]
        row_guides = "Row guides: " + Crucipixel._guide_to_string(self.row_guides)
        col_guides = "Col guides: " + Crucipixel._guide_to_string(self.col_guides)
        total_str = rows_str + [row_guides] + [col_guides]
        return "\n".join(total_str)

if __name__ == '__main__':
    def print_guide(guide):
        for section in guide:
            print(" ".join([str(e) for e in section]))
    row_guides = [[1],[2]]
    col_guides = [[1],[2]]
    cruci = Crucipixel(2,2,row_guides,col_guides)
    cruci[0,0] = Crucipixel.EMPTY
    cruci[0,1] = 1
    cruci[1,1] = 1
    cruci[1,0] = 1
    print(cruci)
    print(cruci.check_ok())
    cruci = Crucipixel(1,6,[[2,2]],[[1],[1],[],[],[1],[1]])
    cruci[0,0] = 1
    cruci[0,1] = 1
    cruci[0,2] = -1
    cruci[0,3] = 1
    cruci[0,4] = 1
    cruci[0,5] = -1
    print(cruci)
    print(cruci.check_ok())
    print_guide(Crucipixel._guide_from_string("1,2;3,4;5,6;0"))
    print("*****************")
    cruci = Crucipixel.guides_from_strings(5, 5, "1;2;3;4;5", "1;2;3;4;5")
    print(cruci)
    
    args = argv[1:]
    with open(args[0],"r") as f:
        cruci = Crucipixel.guides_from_file(f)
    print(cruci)
    