'''
Created on 2011-02-03

@author: jstarke
'''

from django.db import models
from datetime import datetime
from django.core.cache import cache
import threading

import re

class Person(models.Model):
    screen_name = models.CharField(max_length=20,primary_key=True,unique=True)
    user_id = models.IntegerField()
    name = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=200,null=True, blank=True)
    location = models.CharField(max_length=50,null=True, blank=True)
    profile_image_url = models.URLField(null=True, blank=True)
    following_count = models.IntegerField(default=0)
    followers_count = models.IntegerField(default=0)
    since_id = models.BigIntegerField(null=True)
    max_id = models.BigIntegerField(null=True)
    oldest_status_id = models.BigIntegerField(null=True)
    latest_status_id = models.BigIntegerField(null=True)
    last_updated = models.DateTimeField(null=True)
    status_count = models.IntegerField(default=0)
    lock = threading.Lock()
    
    def __unicode__(self):
        return self.screen_name
    
    def __str__(self):
        return self.screen_name
    
    def statuses(self, count=20, offset=0, query=None, **kwargs):
        q = Status.objects.filter(person=self)
        try:
            if query:
                for term in query:
                    q = q.filter(text__icontains=' '+term+' ')
        except:
            print "Error matching this query"
        try:
            if kwargs:
                q = q.filter(**kwargs)
        except:
            pass
        statuses = q.order_by('-created_at').all()[offset:count+offset]
        return statuses
    
    def latestStatus(self):
        person = Person.by_screen_name(self.screen_name)
        return Status.by_id(person.latest_status_id)
    
    def oldestStatus(self):
        person = Person.by_screen_name(self.screen_name)
        return Status.by_id(person.oldest_status_id)
    
    def update(self):
        cache.set('person:' + self.screen_name, self, 300)
        self.save()
        
    def incStatusCount(self,count):
        self.lock.acquire()
        try:
            status_count = cache.get('person_status_count:' + self.screen_name)
            if not status_count:
                status_count = self.status_count
            self.status_count = status_count + count
            cache.set('person_status_count:' + self.screen_name, self.status_count, 300)
        finally:
            self.lock.release()
        
    def statusCount(self):
        count = cache.get('person_status_count:' + self.screen_name)
        if not count:
            count = self.status_count
        return count
            
    
    def setUpdating(self,state):
        self.lock.acquire()
        try:
            cache.set('person_updating:'+ self.screen_name,state,60)
        finally:
            self.lock.release()
        
    def isUpdating(self):
        state = cache.get('person_updating:'+self.screen_name)
        if not state:
            return False
        return state
        
    def expunge(self):
        statuses = Status.objects.filter(person=self).all()
        statuses.delete()
        return self.delete()
    
    @staticmethod
    def by_screen_name(screen_name):
        person = cache.get('person:' + screen_name)
        if not person:
            try:
                person = Person.objects.get(screen_name=screen_name)
                cache.set('person:' + screen_name,person,300)
            except Person.DoesNotExist:
                person = None
        return person
    
    @staticmethod
    def by_id(id):
        person = cache.get('person_id:' + str(id))
        if not person:
            try:
                person = Person.objects.get(user_id=id)
                cache.set('person_id:' + str(id),person,300)
            except Person.DoesNotExist:
                person = None
        return person
            
    
class Status(models.Model):
    status_id = models.BigIntegerField(primary_key=True)
    person = models.ForeignKey(Person)
    in_reply_to_user_id = models.IntegerField(null=True)
    in_reply_to_status_id = models.BigIntegerField(null=True)
    text = models.CharField(max_length=240)
    created_at = models.DateTimeField()
    
    class Meta:
        ordering = ["status_id"]
        
    def status_date(self):
        dt = self.created_at
        return {'year':dt.year, 'month':dt.month, 'day':dt.day}
    
    @staticmethod
    def by_id(id):
        status = cache.get('status:' + str(id))
        if not status:
            try:
                status = Status.objects.get(status_id=id)
                cache.set('status:' + str(id), status, 300)
            except Status.DoesNotExist:
                status = None
        return status
    
    