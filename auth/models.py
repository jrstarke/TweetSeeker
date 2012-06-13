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
from twitter import oauth
import re, httplib
from twitter.utils import *
from django.core.cache import cache

class Account(models.Model):
	username = models.CharField(max_length=40,primary_key=True)
	oauth_token = models.CharField(max_length=200)
	oauth_token_secret = models.CharField(max_length=200)
	rate_limit = models.IntegerField(default=0)
	rate_remaining = models.IntegerField(default=0)
	rate_reset = models.IntegerField(default=0)
	follow_list = models.CharField(max_length=2048)
	next_call = models.IntegerField(default=0)

	def validate(self):
		errors = []
		if self.username and not re.compile('^[a-zA-Z0-9_]{1,40}$').match( \
			self.username):
			errors += ['username']
		return errors

	# django.core.context_processors.auth assumes that an object attached
	# to request.user is always a django.contrib.auth.models.User, which
	# is completely broken but easy to work around
	def get_and_delete_messages(self): pass

	def token(self):
		return oauth.OAuthToken(self.oauth_token, self.oauth_token_secret)

	def is_authorized(self): return is_authorized(self.token())
	
	def __unicode__(self):
		return self.username
	
	def update(self):
		cache.set('user:' + self.pk, self, 3600)
		self.save()
		
	@staticmethod
	def getUser(user_id):
		user = cache.get('user:' + user_id)
		if not user:
			user = Account.objects.get(pk=user_id)
			cache.set('user:' + user_id, user, 3600)
		return user
