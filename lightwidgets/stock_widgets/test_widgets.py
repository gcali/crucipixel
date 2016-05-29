'''
Created on May 20, 2015

@author: giovanni
'''
from lightwidgets.stock_widgets.widget import Widget
from math import pi, sqrt
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.buttons import Button
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.animator import Animator, Slide, StopAnimation, Animation
from lightwidgets.support import string_size
import itertools

class Circle(Widget):
    
    def __init__(self, radius):
        super().__init__(2*radius,2*radius)
        self.radius = radius
        self.ID = "Circle"
    
    def on_draw(self,w,c):
        c.set_source_rgb(0.5,0,0.4)
        c.arc(self.radius,self.radius,self.radius,0,2*pi)
        c.stroke()
    
class Line(Widget):
    
    def __init__(self, startP, endP):
        super().__init__(endP.y,endP.x)
        self.startP = startP
        self.endP = endP
        self.ID = "Line"
    
    def on_draw(self,w,c):
        c.set_line_width(3)
        c.set_source_rgb(0.5,0,0.4)
        c.move_to(self.startP.x,self.startP.y)
        c.line_to(self.endP.x,self.endP.y)
        c.stroke()
    
    def clip_path(self,c):
        width=self.endP.y - self.startP.y
        height=self.endP.x - self.startP.x
        c.rectangle(self.startP.x, self.startP.y,width,height)
        c.clip()
#         print(self,c.clip_extents())

class BorderedString(Widget):
    
    def __init__(self, string:"str"="ciao", font_size=10):
        super().__init__()
        self.string = string
        self.font_size = font_size
    
    
    def on_draw(self, w, c):
        Widget.on_draw(self, w, c)
        c.set_font_size(self.font_size)
        size = string_size(self.font_size,self.string)
        c.save()
        print(size.x,size.y)
        c.rectangle(0,0,size.x,size.y)
        c.stroke()
        c.move_to(0,size.y)
        c.show_text(self.string) 
        import string
        sizes = {}
#         for symbol in itertools.chain(string.ascii_lowercase, string.ascii_uppercase, "0123456789 "):
        for symbol in itertools.chain(",.;-><_!?@'"):
            values = ([],[],[],[])
            for font_size in range(10,20):
                c.set_font_size(font_size)
                for (s,v) in zip(values, c.text_extents(symbol)):
                    s.append(v/font_size)
            sizes[symbol] = [sum(l)/len(l) for l in values]
        with open("textExtents", "w") as f:
            for symbol in sorted(sizes.keys()):
                s = sizes[symbol]
                width = s[0] + s[2]
                height = s[1]
                lower_add = s[1] + s[3]
                if symbol == ' ':
                    print("Hi! {} {} {}".format(width, height, lower_add))
                if lower_add < 1:
                    lower_add = 0
                print("  '{}' : [{},{},{}],".format(symbol, width, -height, lower_add), file=f) 
        c.restore()
            

class Donut(Widget):
    
    def __init__(self, centerP, inner, outer,iters=36):
        super().__init__(outer*2, outer*2)
        self._centerP = Point(0,0)
        self.centerP = centerP
        self.inner = inner
        self.outer = outer
        self.iters = iters
        self.selected = False
        self.ID = "Donut"
    
    def on_draw(self,w,c):
        for i in range(self.iters):
            c.save()
            c.rotate(i*pi/self.iters)
            c.scale(1,self.inner/self.outer)
            c.arc(0,0,self.outer,0,2*pi)
            c.stroke() 
            c.restore()
            
    def on_key_down(self, w, e):
        return Widget.on_key_down(self, w, e)
    
    @property
    def centerP(self):
        return self._centerP

    @centerP.setter
    def centerP(self,value):
        self._centerP= value + self.centerP
        self.translate(value.x,value.y)
        #self.translate(deltaX,deltaY)
    
    def is_point_in(self, p:"Point",*args,**kwargs):
        isInExtern = (sqrt(p.x*p.x + p.y*p.y) <= self.outer)
        isInIntern = (sqrt(p.x*p.x + p.y*p.y) <= self.inner)
        return isInExtern and not isInIntern
    
    def on_mouse_down(self,w,e):
        p = Point(e.x,e.y)
        if self.is_point_in(p):
            self.selected = True 
            self._deltaP = p
            return True
        else:
            return False
    
    def on_mouse_up(self,w,e):
        self.selected = False
        self._deltaP = None
        return True
    
    def on_mouse_move(self,w,e):
        if self.selected:
            self.centerP =  Point(e.x,e.y) - self._deltaP
            w.invalidate()
        return True
    

if __name__ == '__main__':
    main = MainWindow("Animated donut")
    root = Root(600,600)
    root.set_main_window(main)
#     main.add(root)and 
    donut = Donut(Point(200,200), 50, 150)
    circle = Circle(100)
    circle.translate(200,200)
#     button = Button("I'm a button", 100, 50)
#     button.translate(50,50)
    cont_b = UncheckedContainer()
    text = BorderedString("ciao io sono una scritta,    e ho tanti spazi", font_size=20)
    text.translate(20,50)
    cont_b.add(text)
    cont = UncheckedContainer()
    cont.add(donut)
    root.child=cont
    animator = Animator(interval=.01)
    start_point = Point(50,50)
    end_point = Point(350,350)
    speed = Point(200,200)
    duration = 2
    pos = start_point
    def assign(p):
        global pos
        delta_point = p - pos
        donut.centerP = delta_point
        pos = p
    def clean():
        global pos
#         print(pos,start_point)
        new_animation = Slide.calculateAccelerationSpeed(2,
                                                         pos, 
                                                         start_point, 
                                                         assign)
        new_animation.widget = donut
        animator.add_animation(new_animation)
    def clean():
        class ChangeLetter(Animation):
            def __init__(self, letters, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.letters = letters
                self.index = 0
                self.next = 1
            def step(self, next_time):
                current_t = next_time - self.start_time
                if self.next <= current_t:
                    text.string = self.letters[self.index]
                    text.invalidate()
                    self.index += 1
                    self.next += 1
                    if self.index >= len(self.letters):
                        return False
                return True 
        donut.broadcast_lw_signal("change_to_b")
        import string
        letters = list(itertools.chain(string.ascii_letters, "0123456789", " !,;_"))
        animator.add_animation(ChangeLetter(letters))
#         print(root.window_size)
    root.register_switch_to("change_to_b", cont_b)
    animation = Slide.calculateAcceleration(2*duration,
                                            start_point, 
                                            speed, 
                                            assign,
                                            clean)
    animation_stop = StopAnimation(animation=animation,time_offset=1)
    animation.widget = donut
    animator.add_animation(animation)
    animator.add_animation(animation_stop)
#     def assign(d):
#         donut.centerP = d
#     animation = AccMovement(assign=assign,
#                             start_position=Point(0,0),
#                             duration=2,
#                             acc=Point(100,100),
#                             start_speed=Point(0,0))
#     animation.widget = donut
#     animator.add_animation(animation)
    animator.start() 
    main.start_main()