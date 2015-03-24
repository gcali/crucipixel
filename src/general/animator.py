'''
Created on Mar 23, 2015

@author: giovanni
'''
from threading import Lock, Condition, Thread
import time
from general.geometry import Point

class Animator:
    
    def __init__(self,interval=.01,widget=None):
        self.interval = interval
        self._animations = []
        self._lock = Lock()
        self._task_arrived = Condition(self._lock)
        if widget:
            self._widgets = [widget]
        else:
            self._widgets = []
            
    def add_widget(self, widget):
        self._widgets.append(widget)
        
    def remove_widget(self, widget):
        self._widgets.remove(widget)
        
    def start(self):
        self._thread = Thread(target=self,name="animator-thread",daemon=True)
        self._thread.start()
    
    def add_animation(self, animation):
        with self._lock:
            animation.start_time = time.perf_counter()
            self._animations.append(animation)
            self._task_arrived.notify(1)
        
    def _manage_animation(self,animation:"Animation"):
        if animation.stop:
            return False 
        return animation.step(time.perf_counter())
    
    def __call__(self):
        """ Do not call directly
        """
        while True:
            with self._lock:
                while not self._animations:
                    self._task_arrived.wait(None)
                new_animations = []
                for animation in self._animations:
                    if self._manage_animation(animation):
                        new_animations.append(animation)
                for w in self._widgets:
                    w.invalidate()
                self._animations = new_animations
                time.sleep(self.interval) 
    
class Animation:
    
    def __init__(self):
        self.stop = False
        self.start_time = None
    
    def step(self, next_time:"fractional seconds"):
        raise NotImplementedError

    
class Slide(Animation):
    
    def __init__(self,
                 duration,
                 start_point:"Point",
                 end_point:"Point",
                 speed:"Point",
                 assign:"Point -> ()",
                 *args,
                 **kwargs):
        def local_cmp(a,b):
            if a < b:
                return -1
            elif a > b:
                return 1
            else:
                return 0 
        def calc_acc(end,speed,duration):
            return -(speed/duration)
        super().__init__(*args,**kwargs)
        self._assign = assign
        self._duration = duration
        self._start_point = start_point
        self._speed = speed.copy()
        x_acc = calc_acc(speed.x,duration)
        y_acc = calc_acc(speed.y,duration)
        self._acc = Point(x_acc,y_acc)
        print("Start:", start_point.x)
        print("End:", end_point.x)
        print("Speed:", speed.x)
        print("Acc:", x_acc)
        print("Duration:",duration)
    
    
    def step(self, next_time:"fractional seconds"):
        def calc_pos(start,speed,acc,duration):
            return start + duration*(speed + duration*(acc/2))
        retval = True
        current_t = next_time - self.start_time
        if current_t >= self._duration:
            current_t = self._duration
            retval = False
        current_point = Point(calc_pos(self._start_point.x,
                                       self._speed.x,
                                       self._acc.x,
                                       current_t),
                              calc_pos(self._start_point.y,
                                       self._speed.y,
                                       self._acc.y,
                                       current_t)
                              )
        self._assign(current_point)
        return retval

    
if __name__ == '__main__':
    data=[]
    def assign(p):
        data.append(p)
    start_point = Point(0,0)
    end_point = Point(100,100)
    speed = Point(950,950)
    duration = .5
    animation = Slide(duration,
                      start_point,
                      end_point,
                      speed,
                      assign)
    animator = Animator()
    animator.add_animation(animation)
    animator.start()
    time.sleep(duration+.1)
    data = ["{{{},{}}}".format(p.x,p.y) for p in data]
    print("[" + ",".join(data) + "]")