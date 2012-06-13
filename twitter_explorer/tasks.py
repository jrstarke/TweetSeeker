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

from twitter import collector
from twitter.models import Person, Status
from twitter_explorer.queue import AbstractJob
from twitter_explorer import queue
import threading
import datetime

lock = threading.Lock()

class GatherPersonTweets(AbstractJob):
    person = None
    account = None    
    
    def __init__(self,person,account=None):
        self.person = person
        self.account = account
        queue.enqueue(self)
    
    def execute (self):
        try:
            num_statuses = collector.person_update_tweets(self.person, self.account)
            if num_statuses > 0:
                self.person.setUpdating(True)
                if self.account.rate_remaining > 0:
                    queue.enqueue(self)
            else:
                self.person.since_id = self.person.latest_status_id
                self.person.max_id = None
                self.person.update()
                self.person.setUpdating(False)
        except:
            self.person.setUpdating(False)
            
class GetPersonAndTweetsFromID(AbstractJob):
    id = None
    account = None
    
    def __init__(self,id,account=None):
        self.id = id
        self.account = account
        queue.enqueue(self)
    
    def execute(self):
        person = Person.by_id(self.id)
        if not person:
            person = collector.person_by_id(self.id, self.account)
        updatePersonTweets(person,self.account)

class GetTweetIfNotExists(AbstractJob):
    status_id = None
    account = None
    
    def __init__(self,status_id,account=None):
        self.status_id = status_id
        self.account = account
        
    def execute(self):
        status = Status.by_id(self.status_id)
    
            
def updatePersonTweets(person,account):
    lock.acquire()
    try:
        if person.isUpdating() is not True:
            if person.last_updated is None or person.last_updated < datetime.datetime.now()-datetime.timedelta(seconds=60):
                person.setUpdating(True)
                person.status_count = person.status_set.count()
                person.update()
                GatherPersonTweets(person,account)
    finally:
        lock.release()
        