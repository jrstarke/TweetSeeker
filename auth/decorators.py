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

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import Account

def wants_account(f):
	def decorated(*args, **kwargs):
		try: kwargs["account"] = Account.getUser(args[0].session['user_id'])
		except: kwargs["account"] = None
		return f(*args, **kwargs)
	return decorated

def needs_account(url):
	def decorated1(f):
		@wants_account
		def decorated2(*args, **kwargs):
			request = args[0]
			if not kwargs["account"]: 
				request.session['next'] = request.path
				return HttpResponseRedirect(url)
			else: return f(*args, **kwargs)
		return decorated2
	return decorated1
