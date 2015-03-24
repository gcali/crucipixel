'''
Created on Mar 23, 2015

@author: giovanni
'''
from threading import Lock, Condition, Thread
import time
from general.geometry import Point

class Animator:
    
    def __init__(self,interval=.025,widget=None):
        self.interval = interval
        self._animations = []
        self._lock = Lock()
        self._task_arrived = Condition(self._lock)
        self._widget = widget
        
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
                if self._widget:
                    self._widget.invalidate()
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
#         def calc_acc(end,start,speed,duration):
#             return (2*(end - start - speed*duration))/(duration*duration)
        def calc_acc(end,start,speed,duration):
            return -(speed/duration)
        super().__init__(*args,**kwargs)
        self._assign = assign
        self._duration = duration
        self._start_point = start_point
        self._end_point = end_point
        x_speed = speed.x * local_cmp(end_point.x, start_point.x)
        y_speed = speed.y * local_cmp(end_point.y, start_point.y)
        self._speed = Point(x_speed, y_speed)
        x_acc = calc_acc(end_point.x,start_point.x,x_speed,duration)
        y_acc = calc_acc(end_point.y,start_point.y,y_speed,duration)
        self._acc = Point(x_acc,y_acc)
        print("Start:", start_point.x)
        print("End:", end_point.x)
        print("Speed:", x_speed)
        print("Acc:", x_acc)
        print("Duration:",duration)
    
    
    def step(self, next_time:"fractional seconds"):
        def calc_pos(start,speed,acc,duration):
            return start + duration*(speed + duration*(acc/2))
        current_t = next_time - self.start_time
        if current_t >= self._duration:
#             self._assign(self._end_point)
            return False
        current_point = Point(calc_pos(self._start_point.x,
                                       self._speed.x,
                                       self._acc.x,
                                       current_t),
                              calc_pos(self._start_point.y,
                                       self._speed.y,
                                       self._acc.y,
                                       current_t)
                              )
        if self._end_point.x - current_point.x < 0:
            print(current_t)
        self._assign(current_point)
        return True

    
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
    time.sleep(4)
    data = ["{{{},{}}}".format(p.x,p.y) for p in data]
    print("[" + ",".join(data) + "]")