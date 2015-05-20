'''
Created on May 20, 2015

@author: giovanni
'''
from lightwidgets.geometry import Rectangle, RoundedRectangle
import math

class DrawableRectangle(Rectangle):
    
    def draw_on_context(self, context):
        context.rectangle(self.start.x, self.start.y, self.width, self.height)
    
class DrawableRoundedRectangle(RoundedRectangle):
    
    def draw_on_context(self, context):
        pi = math.pi
        context.new_sub_path()
        start_x = self.start.x
        start_y = self.start.y
        radius = self.radius
        width = self.width
        height = self.height
        context.arc(start_x + width - radius, start_y + radius, radius, -pi/2, 0)
        context.arc(start_x + width - radius, start_y + height - radius, radius, 0, pi/2)
        context.arc(start_x + radius, start_y + height - radius, radius, pi/2, pi)
        context.arc(start_x + radius, start_y + radius, radius, pi, 3*pi/2)
        context.close_path() 

