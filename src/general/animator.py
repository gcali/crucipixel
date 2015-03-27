'''
Created on Mar 23, 2015

@author: giovanni
'''
from threading import Lock, Condition, Thread, RLock
import time
from general.geometry import Point
from general.physics import get_speed_from_uniform_acceleration,\
    get_position_from_uniform_acceleration, get_position_from_uniform_speed

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
        print("Animation added")
        
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
                current_animations = list(self._animations)
                self._animations = []
            widgets_to_update = set()
            new_animations = []
            for animation in current_animations:
                if animation.widget:
                    widgets_to_update.add(animation.widget)
                if self._manage_animation(animation):
                    new_animations.append(animation)
                elif animation.clean:
                    animation.clean()
            for w in widgets_to_update:
                w.invalidate()
            for w in self._widgets:
                w.invalidate()
            with self._lock:
                self._animations = self._animations + new_animations
            time.sleep(self.interval) 
    
class Animation:
    
    def __init__(self, clean=None):
        self.stop = False
        self.start_time = None
        self.widget = None
        self.clean = clean
    
    def step(self, next_time:"fractional seconds"):
        raise NotImplementedError

    
class Slide(Animation):
    
    @classmethod
    def calculateAcceleration(cls,
                              duration:"sec",
                              start_point:"Point",
                              speed:"Point",
                              assign:"Point -> ()",
                              clean:"() -> ()"=None,
                              **kwargs):
        def calc_acc(speed,duration):
            return -(speed/duration)
        acc = Point(calc_acc(speed.x,duration),
                    calc_acc(speed.y,duration)
                    )
        return cls(duration=duration,
                   start_point=start_point,
                   speed=speed,
                   acc=acc,
                   assign=assign,
                   clean=clean,
                   **kwargs)
    
    @classmethod
    def calculateAccelerationSpeed(cls,
                                   duration,
                                   start_point:"Point",
                                   end_point:"Point",
                                   assign:"Point -> ()",
                                   **kwargs):
        def calc_speed(start,end,duration):
            return (2*(end - start))/duration
        speed = Point(calc_speed(start_point.x,
                                 end_point.x,
                                 duration),
                      calc_speed(start_point.y,
                                 end_point.y,
                                 duration)
                      )
        print(speed)
        return cls.calculateAcceleration(duration=duration, 
                                         start_point=start_point, 
                                         speed=speed, 
                                         assign=assign,
                                         **kwargs)
        
    
    def __init__(self,
                 duration,
                 start_point:"Point",
                 speed:"Point",
                 acc:"Point",
                 assign:"Point -> ()",
                 **kwargs):
        super().__init__(**kwargs)
        self._assign = assign
        self._duration = duration
        self._start_point = start_point
        self._speed = speed
        self._acc = acc
    
    
    def step(self, next_time:"fractional seconds"):
        if self.stop:
            return False
        def calc_pos(start,speed,acc,duration):
            return start + duration*(speed + duration*(acc/2))
        def new_point(time):
            return Point(calc_pos(self._start_point.x,
                                  self._speed.x,
                                  self._acc.x,
                                  time),
                         calc_pos(self._start_point.y,
                                  self._speed.y,
                                  self._acc.y,
                                  time)
                         )
        current_t = next_time - self.start_time
        if current_t >= self._duration:
            current_point = new_point(self._duration)
            self._assign(current_point)
            return False
        else:
            current_point = new_point(current_t)
            self._assign(current_point)
            return True

class StopAnimation(Animation):
    
    def __init__(self,
                 animation,
                 time_offset,
                 **kwargs):
        super().__init__(**kwargs)
        self.animation = animation
        self.time_offset = time_offset
    
    def step(self, next_time:"fractional seconds"):
        current_t = next_time - self.start_time 
        if current_t >= self.time_offset:
            print("Got here!")
            self.animation.stop = True
            return False
        else:
            return True

class AccMovement(Animation):
    
    def __init__(self,
                 assign:"Point(delta) -> ()",
                 acc:"Point(px/sec^2,px/sec^2)",
                 start_position:"Point",
                 duration:"sec",
                 start_speed:"Point" = Point(0,0),
                 **kwargs):
        
        super().__init__(**kwargs)
        self._assign = assign
        self._acc = acc
        self._duration = duration
        self._start_speed = start_speed
        self._start_position = start_position
        self._last_position = start_position
        self._max_speed = get_speed_from_uniform_acceleration(self._start_speed,
                                                              self._acc,
                                                              self._duration)
        print(self._max_speed)
        self._const_speed = False
    
    def step(self, next_time:"fractional seconds"):
        current_t = next_time - self.start_time
        if not self._const_speed and self._duration > current_t:
            new_position = get_position_from_uniform_acceleration(self._start_position,
                                                                  self._start_speed,
                                                                  self._acc,
                                                                  current_t)
#             print((new_position.x-self._last_position.x)/current_t)
        elif not self._const_speed:
            new_position = get_position_from_uniform_acceleration(self._start_position,
                                                                  self._start_speed,
                                                                  self._acc, 
                                                                  self._duration)
            self._start_position = new_position
            print(new_position)
            new_position = get_position_from_uniform_speed(new_position,
                                                           self._max_speed,
                                                           current_t - self._duration)
            self._const_speed = True
        else:
            new_position = get_position_from_uniform_speed(self._start_position,
                                                           self._max_speed,
                                                           current_t - self._duration)
        delta = new_position - self._last_position
        self._last_position = new_position
        self._assign(delta)
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
    time.sleep(duration+.1)
    data = ["{{{},{}}}".format(p.x,p.y) for p in data]
    print("[" + ",".join(data) + "]")