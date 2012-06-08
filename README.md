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
django's [syncdb command](https://docs.djangoproject.com/en/dev/ref/django-admin/#syncdb) to create the associated tables in the database.
For many of the commands, it is important to place yourself at the base of the project,
and then tell django where it can find the settings file. This can be done using the
`--settings=twitter_explorer.settings` flag.

By default, django is not set up to serve static files, such as the css template used by
TweetSeeker.  To make this work, we have defined a variable in settings called `DEBUG_STATIC_DIR`.
This will tell django's `runserver` to serve these file, while debug is turned on, and we
are working with the development build.

Finally, you should set the [TEMPLATES_DIRS](https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs) variable.  This should be an absolute path
to tell django where it can find all of the templates. This should point to
the layout/templates directory under the project.

At this point, the project should be completely ready to try out.  

To try out the project run django's [runserver command](https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-address-port). 
You can choose the port that you'd like to run it on, but by default, it runs on [localhost:8000](http://localhost:8000).
Like `syncdb` above, use the `--settings` flag to tell django where it can find the settings
in your project.


### Production Build

A production ready system should still have the API settings from the development version
above. If you have not build the development version, go back and do that first. There
are common settings in the development version that will also be used by the production version.

The first step to taking this to production, like with the development build, its
to fill in the settings variables. For this, we have created a settings.py file in the
release folder, that will be used for production releases. 

Like in the Development build above, you will need to set the [SECRET_KEY](https://docs.djangoproject.com/en/dev/ref/settings/#secret-key).
This can be the same as the secret key used in the development build above.

Next you will need to set your [Databases](https://docs.djangoproject.com/en/dev/ref/settings/#databases)
for production use. Again, for performance reasons, we would recommend a more robust.

Before we Like with the development system above, we will now use django's [syncdb command](https://docs.djangoproject.com/en/dev/ref/django-admin/#syncdb) to create the associated tables in the database.
Again, it is important to place yourself at the base of the project,
and then tell django where it can find the settings file. This can be done using the
`--settings=release.settings` flag.

Finally, you should set your [TEMPLATES_DIRS](https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs) variable.
Because this is for a production system, this will likely be different than the one used in the development system, but
again, it should be the absolute path.

At this point, the production version of TweetSeeker is ready to be deployed. If you'd like to try it out,
you can use 

### Deploying TweetSeeker

If you have followed the steps above, you will have a fully prepared django project.

At this point, you can choose any deployment method for django. The options can be found at
[Deploying Django](https://docs.djangoproject.com/en/1.4/howto/deployment/).

I personally have experience deploying django applications with Apache and WSGI, so this is 
what I would recommend. The remainder will deal with deployment with WSGI, so your own experiences
may differ.

 

