'''
Created on Feb 19, 2015

@author: giovanni
'''

class Point:
    
    def __init__(self,*args):
        try:
            self.__init__(*(args[0]))
        except TypeError:
                self.x=args[0]
                self.y=args[1]
    
    @property
    def col(self):
        return self.x
    @property
    def row(self):
        return self.y 
    
    def __add__(self,other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self,other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __str__(self):
        return "({},{})".format(self.x,self.y) 
    
    def __eq__(self,other):
        return self.x == other.x and self.y == other.y

class Rectangle:
    
    def __init__(self,start:"Point",width:"num",height:"num"):
        self.start = start
        self.width = width
        self.height = height
    
    def __str__(self):
        return "[{},w{},h{}]".format(self.start,self.width,self.height)
        