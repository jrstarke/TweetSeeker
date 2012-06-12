TweetSeeker
===========

A research tool to help with on-the-fly collection and exploration of tweets.

Requirements
---------------

* Python 2.7
* Django

This project uses [django](https://www.djangoproject.com/), and was developed 
using [Python 2.7](http://www.python.org/download/). 

Before attempting to use or develop for this system, it is necessary that you 
have a working installation of both.


Getting Started
---------------



### Development build

When you first clone or extract TweetSeeker, the base directory of the project should look something like

     auth/
     layout/
     release/
     static/
     test/
     twitter/
     twitter_explorer/
     .git
     django.wsgi
     LICENSE
     README.md
     
There are three important files that we will be working with to get you up and running.

1. *twitter_explorer/settings.py* : This is where you will locate main configuration for your installation of TweetSeeker, including the important locations and Twitter API keys.
2. *release/settings.py* : This is where you will located the production configuration of your installation of TweetSeeker. We will cover this more in [Production Build](#production-build)
3. *django.wsgi* : This will tell your webserver how to run TweetSeeker. We will cover this more in [Deploying TweetSeeker](#deploying-tweetseeker)

#### Configuring TweetSeeker

To get started, we need to set a number of configuration settings. To do this, first open the file: 

`twitter_explorer/settings.py`

1. Set the 
[SECRET_KEY](https://docs.djangoproject.com/en/dev/ref/settings/#secret-key) for django.

2. Add your Twitter API Keys, so that you will be able to access the Twitter API. 
If you do not currently have a Twitter API key, you can create one by 
[creating a new application](https://dev.twitter.com/apps/new). Set the `TWITTERAUTH_KEY` to your Consumer key,
and `TWITTERAUTH_SECRET` to your Consumer Secret.

3. Set the [Databases](https://docs.djangoproject.com/en/dev/ref/settings/#databases) configuration. For the most 
basic development version, we have set this to an sqlite3 database to get you started. For performance 
reasons, we recommend using a more robust database for heavier uses.

4. Set the [TEMPLATES_DIRS](https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs) variable.  
This should be an absolute path to tell django where it can find all of the templates. This should point to
the `layout/templates` directory under the project. For instance, if your TweetSeeker path was `/home/users/auser/TweetSeeker`,
this would be set to `/home/users/auser/TweetSeeker/layout/templates`.

5. Set the `DEBUG_STATIC_DIR` variable. this sohuld point to the absolute path of the `static` directory within
your TweetSeeker installation. By default, django is not set up to serve static files, such as the css template 
used by TweetSeeker.  To make this work, we have defined a variable in settings called `DEBUG_STATIC_DIR`.
This will tell django's `runserver` how to serve these file, while debug is turned on, and we
are working with the development build.

#### Configuring your environment

Before you can run TweetSeekers commands, you need to tell your environment where it can find TweetSeeker. 
This can be done by setting your `PYTHONPATH` environment variable. 

** Linux, Unix and Mac OS X **

If the path to your TweetSeeker installation is `/home/users/auser/TweetSeeker` you would want to execute 
the following:

If you run `echo $PYTHONPATH`, and you get a blank line, run: 

`export PYTHONPATH=/home/users/auser/TweetSeeker`

Otherwise run: 

`export PYTHONPATH=$PYTHONPATH:/home/users/auser/TweetSeeker`

** Windows **

If the path to your TweetSeeker installation was `C:\Users\aUser\TweetSeeker` you would want to execute 
the following command:

If you run `set PYTHONPATH`, and you get a `Environment Variable PYTHONPATH not defined, run: 

`set PYTHONPATH=C:\Users\aUser\TweetSeeker`

Otherwise run: 

`set PYTHONPATH=%PYTHONPATH%;C:\Users\aUser\TweetSeeker`

#### Initialize the database 

Now we're ready to initialize and sync the database. To do this, you can use 
django's [syncdb command](https://docs.djangoproject.com/en/dev/ref/django-admin/#syncdb) to create the associated tables in the database.
For many of the commands, it is important to place yourself at the base of the project,
and then tell django where it can find the settings file. This can be done using the
`--settings=twitter_explorer.settings` flag.

To complete this, if you're in the base directory of TweetSeeker, you can run the command:

`django-admin syncdb --settings=twitter_explorer.settings`


#### Running TweetSeeker

At this point, the project should be completely ready to try out.  

To try out the project run django's [runserver command](https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-address-port). 
You can choose the port that you'd like to run it on, but by default, it runs on [localhost:8000](http://localhost:8000).
Like `syncdb` above, use the `--settings` flag to tell django where it can find the settings
in your project.

To complete this, if you're in the base directory of TweetSeeker, you can run the command: 

`django-admin runserver --settings=twitter_explorer.settings`


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
you can use `django-admin runserver --settings=release.settings` to run a local copy of it.
You may need to set your python path, if you get a get a message such as `Could not import settings 'release.settings'`.

**Note:** Staticly served resources will not be served by default. Should you want to serve these files for testing purposes, you can 
set the `DEBUG_STATIC_DIR` variable to the absolute path of your static directory on the production
system.  This should not be used for more than testing the production installation, and these
static resources should instead be served by the webserver directly. See deploying TweetSeeker below for more details.

### Deploying TweetSeeker

If you have followed the steps above, you will have a fully prepared django project.

At this point, you can choose any deployment method for django. The options can be found at
[Deploying Django](https://docs.djangoproject.com/en/1.4/howto/deployment/).

I personally have experience deploying django applications with Apache and WSGI, so this is 
what I would recommend. The remainder will deal with deployment with WSGI, so your own experiences
may differ.

I will also assume that you're are hosting with an Apache server, again, because that's what I have
experience with. If you don't already have an Apache server, I recommend [Ubuntu Server](http://www.ubuntu.com/download/server), 
as I have always found it fast and easy to install and deploy. To use WSGI, you will want to
also install Apache's WSGI module.

Before setting up the virtual server configuration, you will want to set up your `django.wsgi`
configuration to correctly respond to requests.  This file is fairly generic, so you should
only need to set the `path = '[Base path of TweetSeeker]'` to the proper location.

Next you will want to define your Apache Virtual Server configuration. To get started, you can use
the following overly simplified example.

```
<VirtualHost *:80>
             DocumentRoot /path/to/TweetSeeker

             ServerName your.server.name

             Alias /robots.txt /path/to/TweetSeeker/static/robots.txt
             Alias /favicon.ico /path/to/TweetSeeker/static/favicon.ico

             Alias /static/ /path/to/TweetSeeker/static/

             WSGIScriptAlias / /path/to/TweetSeeker/django.wsgi
</VirtualHost>
```

In the above example, you will need to change `/path/to/TweetSeeker` to the actual path of
the base instalation of TweetSeeker.  For our purposes, we have defined a server name
that the system will respond to.  This can be changed to a port by telling Apache to respond
to the port using the `Listen` setting in the Apache config, and changing `<VirtualHost *:80>` to `<VirtualHost *:[your port]>` 
in the Virtual Server Configuration.

Your installation, if everything has worked properly, should now be working as expected.

