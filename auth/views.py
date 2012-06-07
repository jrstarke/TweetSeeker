from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from twitter.utils import *
from models import Account
from decorators import wants_account, needs_account

@wants_account
def Login(req, account=None):
	if account: return HttpResponseRedirect('/')
	# This url represents the host address
	url = req.build_absolute_uri().replace(req.get_full_path(),'')
	logging.warning(url)
	token = get_unauthorized_token(callback=url+settings.TWITTERAUTH_CALLBACK)
	req.session['token'] = token.to_string()
	return HttpResponseRedirect(get_authorization_url(token,callback=url+settings.TWITTERAUTH_CALLBACK))

@wants_account
def LoginPage(request,account=None):
	return render_to_response('login.html', {'user':account})

def Callback(req):
	session = req.session
	token = None
	if session.has_key('token'):
		token = session['token']
	if not token:
		return render_to_response('auth-callback.html', {
			'token': True
		})
	token = oauth.OAuthToken.from_string(token)
	if token.key != req.GET.get('oauth_token', 'no-token'):
		return render_to_response('auth-callback.html', {
			'mismatch': True
		})
	token = get_authorized_token(token)

	# Actually login
	obj = is_authorized(token)
	if obj is None:
		return render_to_response('auth-callback.html', {
			'username': True
		})
	user = Account.objects.get_or_create(username=obj['screen_name'])[0]
	ratelimits = get_rate_limit(token)
	user.oauth_token = token.key
	user.oauth_token_secret = token.secret
	user.rate_remaining = 350
	user.rate_reset = ratelimits['reset_time_in_seconds']
	user.update()
	session['user_id'] = user.pk
	del req.session['token']
	if session.has_key('next'):
		return HttpResponseRedirect(session['next'])
	else:
		return HttpResponseRedirect('/')
	
@wants_account
def Logout(req, account=None):
	if account is not None:
		account.oauth_token = ''
		account.oauth_token_secret = ''
		account.update()
	req.session.flush()
	return render_to_response('auth-logout.html', {})

def RedirectSlash(req):
	pathuri = req.get_full_path()[0:-1]
	if req.META.has_key('QUERY_STRING'):
		pathuri += "?" + req.META['QUERY_STRING']
	return HttpResponseRedirect(pathuri)
	

