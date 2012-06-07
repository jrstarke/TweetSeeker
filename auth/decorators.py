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
