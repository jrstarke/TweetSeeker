TweetSeeker
===========

A research tool to help with on-the-fly collection and exploration of tweets.

Requirements
---------------

This project uses [django](https://www.djangoproject.com/), and was developed 
using [Python 2.7](http://www.python.org/download/). 

Before attempting to use or develop for this system, it is necessary that you 
have a working installation of both.


Getting Started
---------------

### Development build

To get started with a development build, you will need to set a number of settings 
in the settings.py file, located within twitter_explorer.

First and foremost, you should set the 
[SECRET_KEY](https://docs.djangoproject.com/en/dev/ref/settings/#secret-key) for django.

Next, to be able to access the Twitter API, you will need to add your twitter API keys. 
If you do not currently have a Twitter API key, you can create one by 
[creating a new application](https://dev.twitter.com/apps/new).