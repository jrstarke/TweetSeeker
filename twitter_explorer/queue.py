'''
Created on 2011-04-19

@author: jstarke
'''
import collections
import threading
from multiprocessing import Pool

maxThreads = 50
currentThreads = 0
queue = collections.deque()

lock = threading.Lock()
    
def enqueue(job):
    global queue
    global maxThreads
    global currentThreads
    
    lock.acquire()
    try:
        queue.append(job)
        
        if currentThreads < maxThreads:
            #create a worker
            worker = Worker()
            worker.start()
            currentThreads = currentThreads + 1
    finally:
        lock.release()

def dequeue():
    global queue
    lock.acquire()
    try:
        result = queue.popleft()
    except IndexError:
        result = None
    finally:
        lock.release()
    return result

def loseWorker():
    global currentThreads
    lock.acquire()
    try:
        currentThreads = currentThreads - 1
    finally:
        lock.release()


class Worker (threading.Thread):
    def run (self):
        try:
            while True:
                job = dequeue()
                if job is not None:
                    job.execute()
                else:
                    break
        finally:
            loseWorker()
        
        
class AbstractJob:
    """Jobs for queue. These should all implement the execute method so that the worker can run them"""
    
    def execute(self): 
        """Runs the function that the job specifies"""
        raise NotImplementedError("Should have implemented this")