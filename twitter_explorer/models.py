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

from django.db import models
from twitter.models import Person, Status
from django.core.cache import cache
from auth.models import Account
from datetime import datetime
import re

class Group(models.Model):
    short_name = models.CharField(max_length=40)
    user = models.ForeignKey(Account)
    name = models.CharField(max_length=40)
    members = models.ManyToManyField(Person)
    oldest_status_id = models.BigIntegerField(null=True)
    latest_status_id = models.BigIntegerField(null=True)
    updating = models.BooleanField(default=False)
    inclusive = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ("short_name", "user")
        
    def latestStatus(self):
        latest_status_id = None
        for member in self.members_list():
            if latest_status_id is None or latest_status_id < member.latest_status_id:
                latest_status_id = member.latest_status_id
        return Status.by_id(latest_status_id)
    
    def oldestStatus(self):
        oldest_status_id = None
        for member in self.members_list():
            if oldest_status_id is None or oldest_status_id > member.oldest_status_id:
                oldest_status_id = member.oldest_status_id
        return Status.by_id(oldest_status_id)
     
    def isUpdating(self):
        for member in self.members_list():
            if member.isUpdating():
                return True
        return False
        
    def update(self):
        cache.set('group:' + self.short_name + '+' + self.user.username, self, 300)
        self.save()
        
    def statuses(self, count=20, offset=0, query=None, **kwargs):
        q = Status.objects.filter(person__in=self.members.all())
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
            print "Uh oh, group statuses failed :("
        statuses = q.order_by('-created_at').all()[offset:count+offset]
        return statuses
    
    def members_list(self):
        members = cache.get('group_members:'+ self.short_name + '+' + self.user.username)
        if not members:
            members = self.members.all()
            cache.set('group_members:'+ self.short_name+'+'+ self.user.username, members, 300)
        return members
    
    def status_count(self):
        count = 0
        for member in self.members.all():
            count = count + member.status_count
        return count 
    
    @staticmethod
    def by_short_name_and_user(short_name,user):
        group = cache.get('group:' + short_name + "+" + user.username)
        if not group:
            try:
                group = Group.objects.get(short_name=short_name,user=user)
            except Group.DoesNotExist:
                group = None
            cache.set('group:' + short_name + '+' + user.username, group, 300)
        return group

    @staticmethod
    def by_user(user):
        groups = Group.objects.filter(user=user).all()
        return groups
    