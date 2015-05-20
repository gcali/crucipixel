'''
Created on Feb 19, 2015

@author: giovanni
'''
import math

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
    
    @property
    def norm(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    
    def copy(self):
        return Point(self.x,self.y)
    
    def __add__(self,other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self,other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __str__(self):
        return "({},{})".format(self.x,self.y) 
    
    def __eq__(self,other):
        return self.x == other.x and self.y == other.y

class Rectangle:
    
    @staticmethod
    def from_points(point_iter:"iterable of Point") -> "Rectangle":
        minX = float("inf")
        minY = float("inf")
        maxX = float("-inf")
        maxY = float("-inf")
        for p in point_iter:
            minX = min(p.x,minX)
            minY = min(p.y,minY)
            maxX = max(p.x,maxX)
            maxY = max(p.y,maxY)
        return Rectangle(Point(minX,minY),maxX-minX,maxY-minY)
    
    def __init__(self,start:"Point",width:"num",height:"num"):
        self.start = start
        self.width = width
        self.height = height
    
    def __str__(self):
        return "[{},w{},h{}]".format(self.start,self.width,self.height)
    
    def is_point_in(self,p:"Point",delta=0):
        if self.width >= 0:
            x_ok = (p.x >= self.start.x-delta and p.x <= self.start.x + self.width+delta)
        else:
            x_ok = (p.x <= self.start.x+delta and p.x >= self.start.x + self.width-delta)
        if self.height >= 0:
            y_ok = (p.y >= self.start.y-delta and p.y <= self.start.y + self.height+delta)
        else:
            y_ok = (p.y <= self.start.y+delta and p.y >= self.start.y + self.height-delta)
        return x_ok and y_ok
    
    def get_vertexes(self):
        return [self.start,
                Point(self.start.x + self.width,self.start.y),
                Point(self.start.x,self.start.y + self.height),
                Point(self.start.x + self.width,self.start.y + self.height)
                ]
        

class RoundedRectangle:
    
    def __init__(self, start:"Point", width, height, radius=None):
        self.start = start
        self.width = width
        self.height = height
        self._radius = radius
    
    @property
    def radius(self):
        if self._radius is None:
            return min(self.width / 2, self.height / 2, 10)
        else:
            return self._radius
    @radius.setter
    def radius(self,value):
        self._radius = value
    
    def is_point_in(self, p:"Point",delta=0):
        main_rectangle = Rectangle(self.start, self.width, self.height)
        radius = self.radius
        if not main_rectangle.is_point_in(p):
            return False
        thin_rectangle = Rectangle(Point(self.start.x + radius, self.start.y), 
                                   self.width - 2*radius, 
                                   self.height)
        if thin_rectangle.is_point_in(p):
            return True
        short_rectangle = Rectangle(Point(self.start.x, self.start.y + radius),
                                    self.width,
                                    self.height - 2*radius)
        if short_rectangle.is_point_in(p):
            return True 
        def check_circle(p:"Point", center:"Point", radius):
            return (p.x - center.x)**2 + (p.y - center.y)**2 <= radius**2
        if check_circle(p, Point(radius,radius), radius):
            return True
        elif check_circle(p, Point(self.start.x + self.width - radius, radius), radius):
            return True
        elif check_circle(p, Point(self.start.x + self.width - radius,
                                   self.start.y + self.height - radius),
                          radius):
            return True
        elif check_circle(p, Point(radius, self.start.y + self.height - radius), radius):
            return True
        return False

    def get_vertexes(self):
        return [self.start,
                Point(self.start.x + self.width,self.start.y),
                Point(self.start.x,self.start.y + self.height),
                Point(self.start.x + self.width,self.start.y + self.height)
                ]
