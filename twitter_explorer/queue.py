'''
Copyright 2011-2012 Jamie Starke, The CHISEL group and contributors

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
  
    Contributors
         Jamie Starke
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