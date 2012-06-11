import os
import sys

# This defines the settings used for release configuration
os.environ['DJANGO_SETTINGS_MODULE'] = 'release.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# this is the path to your project so that it can find the enviroment above
path = '/home/jstarke/TweetSeeker'
if path not in sys.path:
    sys.path.append(path)
