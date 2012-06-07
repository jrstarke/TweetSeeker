# Taken almost verbatim from Henrik Lied's django-twitter-oauth app
# http://github.com/henriklied/django-twitter-oauth
# This file has been used and included with the permission of Henrik

from django.utils import simplejson as json
import oauth
import httplib
import logging
import sys
from twitter_explorer import settings
import urllib
from django.utils import simplejson

signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

TWITTERAUTH_KEY = settings.TWITTERAUTH_KEY
TWITTERAUTH_SECRET = settings.TWITTERAUTH_SECRET
TWITTERAUTH_CALLBACK = settings.TWITTERAUTH_CALLBACK

def consumer():
	try: return consumer._consumer
	except AttributeError:
		consumer._consumer = oauth.OAuthConsumer(TWITTERAUTH_KEY, TWITTERAUTH_SECRET)
		return consumer._consumer

def proxy_connection():
	try: return connection._connection
	except AttributeError:
		connection._connection = httplib.HTTPSConnection('tweet-seeker.appspot.com')
		return connection._connection
	
def connection():
	try: return connection._connection
	except AttributeError:
		connection._connection = httplib.HTTPSConnection('twitter.com')
		return connection._connection

def oauth_request(
	url,
	token,
	parameters=None,
	signature_method=signature_method,
	http_method='GET'
):
	req = oauth.OAuthRequest.from_consumer_and_token(
		consumer(), token=token, http_url=url,
		parameters=parameters, http_method=http_method
	)
	req.sign_request(signature_method, consumer(), token)
	return req

def oauth_response(req):
	# Pass this through the URL proxy
	connection = httplib.HTTPSConnection('twitter.com')
	connection.request(req.http_method, req.to_url())
	resp = connection.getresponse()
	response = resp.read(), resp.getheaders()
	connection.close()
	return response

def get_unauthorized_token(signature_method=signature_method, callback=TWITTERAUTH_CALLBACK):
	req = oauth.OAuthRequest.from_consumer_and_token(
		consumer(), http_url='https://api.twitter.com/oauth/request_token', callback=callback
	)
	req.sign_request(signature_method, consumer(), None)
	return oauth.OAuthToken.from_string(oauth_response(req)[0])

def get_authorization_url(token, signature_method=signature_method, callback=TWITTERAUTH_CALLBACK):
	req = oauth.OAuthRequest.from_consumer_and_token(
		consumer(), token=token,
		http_url='https://api.twitter.com/oauth/authorize', 
		callback=callback
	)
	req.sign_request(signature_method, consumer(), token)
	return req.to_url()

def get_authorized_token(token, signature_method=signature_method):
	req = oauth.OAuthRequest.from_consumer_and_token(
		consumer(), token=token,
		http_url='https://api.twitter.com/oauth/access_token'
	)
	req.sign_request(signature_method, consumer(), token)
	return oauth.OAuthToken.from_string(oauth_response(req)[0])

def api(url, token, http_method='GET', **kwargs):
	try:
		result, headers= oauth_response(oauth_request(
			url, token, http_method=http_method, parameters=kwargs
		))
		j = json.loads(result)
		return j, headers
	except Exception, e:
		type, value, traceback = sys.exc_info()
		logging.exception("An Exception Occurred while trying to access URL: "+ url)								
	return None,None

def is_authorized(token):
	return api('https://twitter.com/account/verify_credentials.json',
		token)[0]
		
def get_rate_limit (token):
	result, headers = api('https://api.twitter.com/1/account/rate_limit_status.json', token)
	return result
	
	