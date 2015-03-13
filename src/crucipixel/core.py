'''
Created on Mar 13, 2015

@author: giovanni
'''
from itertools import zip_longest

class Crucipixel:
    
    EMPTY=-1
    DEFAULT=0
    
    def __init__(self,rows:"int >0",cols:"int >0",
                 row_guides:"iter of iter of int >0",
                 col_guides:"iter of iter of int >0"):
        self.rows = rows
        self.cols = cols
        self.row_guides = [list(row) for row in row_guides]
        self.col_guides = [list(col) for col in col_guides]
        self._matrix = [[Crucipixel.DEFAULT for j in range(self.cols)] for i in range(self.rows)]  # @UnusedVariable 
    
    def check_ok(self):
        def check_line(line,guide):
            minimal_line=[]
            start_new=True
            count=0
            for i in range(len(line)):
                if line[i] == Crucipixel.DEFAULT:
                    return True
                if line[i] != Crucipixel.EMPTY:
                    count += 1
                    start_new = False
                elif not start_new:
                    minimal_line.append(count)
                    count=0
                    start_new = True
            if count != 0:
                minimal_line.append(count)
            for r,g in zip_longest(minimal_line,guide):
                if r != g:
                    return False
            return True 

        for row,guide in zip(self._matrix,self.row_guides):
            if not check_line(row,guide):
                return False
        for col,guide in zip([[self[i,j] for i in range(self.rows)] for j in range(self.cols)],self.col_guides):
            if not check_line(col,guide):
                return False
        return True
    
    def guides_from_string(self,string):
        pass
    
    def __getitem__(self,key):
        i,j = key
        return self._matrix[i][j]
    
    def __setitem__(self,key,value):
        i,j = key
        self._matrix[i][j] = value
    
    def __str__(self):
        rows_str = [" ".join([str(self[i,j]).rjust(2) for j in range(self.cols)])\
                for i in range(self.rows)]
        return "\n".join(rows_str)

if __name__ == '__main__':
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
    