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

Next your [Databases](https://docs.djangoproject.com/en/dev/ref/settings/#databases) should be configured. For the most basic development version, 
you can use sqlite3. For performance reasons, we recommend using a more robust 
database for heavier uses.

Once your database settings are in place, you can use 
django's [syncdb command](https://docs.djangoproject.com/en/dev/ref/django-admin/#syncdb) to create the associated database and tables.

Finally, you should set the [TEMPLATES_DIRS](https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs) variable.  This should be an absolute path
to tell django where it can find all of the templates. This should point to
the layout/templates directory under the project.

At this point, the project should be completely ready to try out.  

To try out the project run django's [runserver command](https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-address-port). 
You can choose the port that you'd like to run it on, but by default, it runs on [localhost:8000](http://localhost:8000).
