from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Auth urls
    (r'^login$','auth.views.LoginPage'),
    (r'^auth/login$','auth.views.Login'),
    (r'^login/callback.*','auth.views.Callback'),
    (r'^logout$','auth.views.Logout'),
    #(r'^.*/$','auth.views.RedirectSlash'),
    
    # Twitter explorer
    (r'^$', 'twitter_explorer.views.MainPage'),
    (r'^about$', 'twitter_explorer.views.AboutPage'),
    (r'^user/(?P<screen_name>[a-zA-Z0-9_]{1,20})$', 'twitter_explorer.views.PersonPage'),
    (r'^user/(?P<screen_name>[a-zA-Z0-9_]{1,20})/tweets-background$', 'twitter_explorer.views.PersonTweetsBackground'),
    (r'^user/(?P<screen_name>[a-zA-Z0-9_]{1,20})/tweets/(?P<loadCount>[0-9]{1,4})$', 'twitter_explorer.views.PersonTweetsAdditional'),
    (r'^user/(?P<screen_name>[a-zA-Z0-9_]{1,20})/tweets$', 'twitter_explorer.views.PersonTweets'),
    (r'^user$', 'twitter_explorer.views.UserRedirect'),
    
    (r'^group$', 'twitter_explorer.views.GroupListPage'),
    (r'^group-add$', 'twitter_explorer.views.GroupAddPage'),
    (r'^group-add/generate$', 'twitter_explorer.views.GroupGenAddPage'),
    (r'^group/(?P<short_name>[a-zA-Z0-9_]{1,20})$', 'twitter_explorer.views.GroupPage'),
    (r'^group/(?P<short_name>[a-zA-Z0-9_]{1,20})/tweets-background$', 'twitter_explorer.views.GroupTweetsBackground'),
    (r'^group/(?P<short_name>[a-zA-Z0-9_]{1,20})/tweets/(?P<loadCount>[0-9]{1,4})$', 'twitter_explorer.views.GroupTweetsAdditional'),
    (r'^group/(?P<short_name>[a-zA-Z0-9_]{1,20})/tweets$', 'twitter_explorer.views.GroupTweets'),
    
    (r'^status/(?P<status_id>[0-9]{1,30})$', 'twitter_explorer.views.Tweet'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
    (r'^static/(?P<path>.*)$', 
        'serve', {
        'document_root': 'C:/Users/jstarke/Development/hg-projects/jamies-repo/twitter_explorer/src/static',
        'show_indexes': True }),)

