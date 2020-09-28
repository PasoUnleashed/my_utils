import datetime
import numpy as np
import random
from calendar import monthrange


class PriorityQueue(object): 
    def __init__(self,evaluator = lambda a,b : a>b): 
        self.queue = [] 
        self.evaluator = evaluator
  
    def __str__(self): 
        return ' '.join([str(i) for i in self.queue]) 
  
    # for checking if the queue is empty 
    def isEmpty(self): 
        return len(self.queue) == 0
  
    # for inserting an element in the queue 
    def insert(self, data): 
        self.queue.append(data) 
  
    # for popping an element based on Priority 
    def delete(self): 
        try: 
            max_element = 0
            for i in range(len(self.queue)): 
                if self.evaluator(self.queue[i] , self.queue[max_element]): 
                    max_element = i 
            item = self.queue[max_element] 
            del self.queue[max_element] 
            return item 
        except IndexError: 
            print() 
            exit() 


class StopWatch:
    def __init__(self):
        self.start_time=None
        self.end = None
    def start(self,time =None):
        if(time):
            self.start_time = time
        else:
            self.start_time = datetime.datetime.now()
    def stop(self,time=None):
        if(time):
            self.end = time
        else:
            self.end = datetime.datetime.now()
    def mesure_ms(self,time=None):
        return self.mesure().total_seconds()*1000
    def mesure(self,time=None):
        if(self.start_time==None):
            return datetime.timedelta(seconds=0)
        if(time!=None):
            return (time-self.start_time)
        if(self.end!=None):
            return (self.end-self.start_time)
        return (datetime.datetime.now()-self.start_time)
class Acumulator:
    vals = []
    weights = []
    def __init__(self,max_length=0):
        self.max_length=max_length
    def add(self,value,weight=1):
        self.vals.append(value)
        self.weights.append(weight)
        if(self.max_length> 0 and len(self.vals)>self.max_length):
            self.vals.pop(0)
            self.weights.pop(0)
    def avg(self):
        return np.average(self.vals,0,weights = self.weights)
    def median(self):
        return np.median(self.vals,0)
    def total(self):
        return np.sum(self.vals,0)
    @classmethod
    def __len__(cls):
        return len(cls.vals)
class FrameRateReg:
    def __init__(self,fps):
        self.fps = fps
        self.last_frame = datetime.datetime(1,1,1)
        self.wait_time = datetime.timedelta(milliseconds=1000/fps)
    def wait_for_next(self):
        while(not self.is_frame_time()):
            pass
    def is_frame_time(self):
        if(datetime.datetime.now()-self.last_frame>self.wait_time):
            self.last_frame=datetime.datetime.now()
            return True
        return False
def get_time_encoding(time):
    second=time.minute*60
    second+=time.second
    second+=time.hour*60*60
    secs_in_day = 60*60*24 
    sx = np.sin(2*np.pi*(second/secs_in_day))
    sy = np.cos(2*np.pi*(second/secs_in_day))
    dx = np.sin(2*np.pi*(time.day/monthrange(time.year,time.month)[1]))
    dy = np.cos(2*np.pi*(time.day/monthrange(time.year,time.month)[1]))
    mx = np.sin(2*np.pi*(time.month/12))
    my = np.cos(2*np.pi*(time.month/12))
    dowx= np.sin(2*np.pi*((time.weekday()+1)/7))
    dowy= np.sin(2*np.pi*((time.weekday()+1)/7))
    return [sx,sy,dx,dy,mx,my,dowx,dowy]