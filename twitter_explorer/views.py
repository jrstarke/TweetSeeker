'''
Created on 2011-02-03

@author: jstarke
'''
from django.shortcuts import render_to_response 
from django.template.loader import render_to_string
from twitter.models import Person, Status
from twitter_explorer.models import Group
from django.http import HttpResponse, HttpResponseRedirect
from auth.decorators import wants_account, needs_account
from django.utils import simplejson
from twitter_explorer import settings
from twitter import collector
from datetime import datetime
from django.template.context import RequestContext
from twitter_explorer import tasks
import time
import sys, traceback
import re
import urllib2

def encodeURLs(statuses,account):
    r = re.compile(r"(http://[^, ]+[^,. ])")
    s = re.compile(r'(\A|\s)@(\w+)')
    if isinstance(statuses,Status):
        temp = []
        temp.append(statuses)
        statuses = temp
    for status in statuses:
        status.text = r.sub(r'<a href="\1" target="_blank" rel="nofollow">\1</a>', status.text)
        status.text = s.sub(r'\1@<a href="/user/\2" target="_blank" rel="nofollow">\2</a>', status.text)

@wants_account
def MainPage(request,account=None):
    return render_to_response('index.html',{'user':account})

@wants_account
def PersonPage(request,screen_name,account=None):
    if account:
        person = collector.person(screen_name,account)
    else:
        person = Person.by_screen_name(screen_name)
    if person:
        tasks.updatePersonTweets(person,account)
        num_friends = person.following_count
    else:
        num_friends = None
    return render_to_response('person.html',{'person':person,
                                      'num_friends':num_friends,
                                      'user':account})
    
@wants_account
def PersonTweets(request,screen_name,account=None):
    person = Person.by_screen_name(screen_name)
    filters = {}
    terms=None
    if request.REQUEST.get('start'):
        filters['created_at__gte'] = datetime.strptime(request.REQUEST.get('start'),"%Y-%m-%d")
    if request.REQUEST.get('end'):
        filters['created_at__lt'] = datetime.strptime(request.REQUEST.get('end'),"%Y-%m-%d")
    if request.REQUEST.get('q'):
        terms = request.REQUEST.get('q').split()
    statuses = person.statuses(20,0,query=terms,**filters)
    encodeURLs(statuses, account)
    return render_to_response('person-tweets.html', {'screen_name':screen_name, 'statuses':statuses})

@wants_account
def PersonTweetsAdditional(request,screen_name,loadCount=0,account=None):
    person = Person.by_screen_name(screen_name)
    filters = {}
    tweetCount = 20
    loadCount = tweetCount * int(loadCount)
    terms = None
    if request.REQUEST.get('start'):
        filters['created_at__gte'] = datetime.strptime(request.REQUEST.get('start'),"%Y-%m-%d")
    if request.REQUEST.get('end'):
        filters['created_at__lt'] = datetime.strptime(request.REQUEST.get('end'),"%Y-%m-%d")
    if request.REQUEST.get('q'):
        terms = request.REQUEST.get('q').split()
    statuses = person.statuses(tweetCount,loadCount,query=terms,**filters)
    encodeURLs(statuses, account)
    return render_to_response('person-tweets-additional.html', {'screen_name':screen_name, 'statuses':statuses})

@wants_account
def PersonTweetsBackground(request,screen_name,account=None):
    try:
        output = {}
        person = Person.by_screen_name(screen_name)
        count = 0
            
        while person.statusCount() is 0 and person.isUpdating() is True:
            time.sleep(2**count)
            count = count + 1
            
        complete = not person.isUpdating()
          
        output['num_statuses'] = person.statusCount()
        output['complete'] = complete
        
        if person.oldestStatus():
            output['oldest_date'] = person.oldestStatus().status_date()
        if person.latestStatus():
            output['latest_date'] = person.latestStatus().status_date()
        
        if account:
            output['api_calls'] = account.rate_remaining
        response = HttpResponse()
        response.write(simplejson.dumps(output))
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "*** print_tb:"
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print "*** print_exception:"
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
        print "*** print_exc:"
        traceback.print_exc()
        print "*** format_exc, first and last line:"
    return response
       
@wants_account
def AboutPage(request,account=None):
    return render_to_response('about.html', {'user':account})

@needs_account('/login')
def GroupListPage(request,account=None):
    groups = Group.by_user(account)
    return render_to_response('group-list.html', {'user':account,
                                             'groups':groups,
                                             })

@needs_account('/login')
def GroupAddPage(request,account=None):
    name = request.REQUEST.get('name','')
    short_name = name.replace(' ','_').lower()
    member_names = request.REQUEST.get('member_names','')
    auto_gen = request.REQUEST.get('auto_gen',None)
    
    errors = []
    
    if 'POST' == request.method:
        if auto_gen:
            return render_to_response('group-add.html', {
                                                        "user": account,
                                                        "member_names":member_names,
                                                        }, context_instance=RequestContext(request))
        group = Group.by_short_name_and_user(short_name, account)
        if group:
            return render_to_response('group-add.html', {
                                                        "errors":['A group by the short_name \'' + short_name + '\' already exists for you. Please try another.'], 
                                                        "user": account, 
                                                        "short_name":short_name, 
                                                        "name":name,
                                                        "member_names":member_names,
                                                        }, context_instance=RequestContext(request))
        people = []
        if len(short_name) < 1:
            errors.append("Please ensure the group name is atleast 1 character long.")
        for member in member_names.strip().split(','):
            person = Person.by_screen_name(member)
            if not person:
                person = collector.person(member,account)
            if person:
                people.append(person)
                tasks.updatePersonTweets(person,account)
            else:
                errors.append("Could not find a user named: " + member)
        if len(errors) > 0:
            return render_to_response('group-add.html', {
                                                        "errors":errors, 
                                                        "user": account, 
                                                        "short_name":short_name, 
                                                        "name":name,
                                                        "member_names":member_names,
                                                        }, context_instance=RequestContext(request))
        else:
            group = Group.objects.create(short_name=short_name, user=account, name=name)
            for person in people:
                group.members.add(person)
            group.save()
            return HttpResponseRedirect('/group')
    return render_to_response('group-add.html', {
                                            'user': account, 
                                            },context_instance=RequestContext(request))
       
@needs_account('/login')
def GroupGenAddPage(request,account=None):
    
    errors = []
    
    if 'POST' == request.method:
        url = request.REQUEST.get('url','')
        
        try:
            conn = urllib2.urlopen(url)
            data = conn.read()
            conn.close()
        except:
            errors.append('We were unable to get any data from the url provided. Please make sure it is correct and includes the http://')
        
        if len(errors) > 0:
            return render_to_response('group-gen-add.html', {
                                                             'url':url,
                                                             'errors':errors,
                                                             'user':account,
                                                             }, context_instance=RequestContext(request))
            
        r = re.compile(r"(twitter.com/[^, /\"]+[^,. /\"])")
        links = r.findall(data)
        members = []
        for link in links:
            link = link.replace('twitter.com/','')
            if not link in members:
                person = collector.person(link, account)
                if person: 
                    members.append(link)
        
        member_names = ""
        for member in members:
            if len(member_names) > 0:
                member_names = member_names + ","
            member_names = member_names + member
        
        return render_to_response('group-gen-add.html', {
                                                         'user':account,
                                                         'member_names':member_names}, context_instance=RequestContext(request))
            
    return render_to_response('group-gen-add.html', {
                                                     'user':account,
                                                     }, context_instance=RequestContext(request))
       
@needs_account('/login')
def GroupPage(request,short_name,account=None):
    group = Group.by_short_name_and_user(short_name, account)
    for member in group.members.all():
        tasks.updatePersonTweets(member, account)
    return render_to_response('group.html',{'group':group,
                                      'user':account})
    
@wants_account
def GroupTweets(request,short_name,account=None):
    group = Group.by_short_name_and_user(short_name, account)
    terms = None
    filters = {}
    if request.REQUEST.get('start'):
        filters['created_at__gte'] = datetime.strptime(request.REQUEST.get('start'),"%Y-%m-%d")
    if request.REQUEST.get('end'):
        filters['created_at__lt'] = datetime.strptime(request.REQUEST.get('end'),"%Y-%m-%d")
    if request.REQUEST.get('q'):
        terms = request.REQUEST.get('q').split()
    statuses = group.statuses(20,0,query=terms,**filters)
    encodeURLs(statuses, account)
    return render_to_response('group-tweets.html', {'name':group.name, 'statuses':statuses})

@wants_account
def GroupTweetsAdditional(request,short_name,loadCount=0,account=None):
    group = Group.by_short_name_and_user(short_name, account)
    filters = {}
    terms = None
    tweetCount = 20
    loadCount = tweetCount * int(loadCount)
    if request.REQUEST.get('start'):
        filters['created_at__gte'] = datetime.strptime(request.REQUEST.get('start'),"%Y-%m-%d")
    if request.REQUEST.get('end'):
        filters['created_at__lt'] = datetime.strptime(request.REQUEST.get('end'),"%Y-%m-%d")
    if request.REQUEST.get('q'):
        terms = request.REQUEST.get('q').split()
    statuses = group.statuses(tweetCount,loadCount,query=terms,**filters)
    encodeURLs(statuses, account)
    return render_to_response('group-tweets-additional.html', {'statuses':statuses})

@wants_account
def GroupTweetsBackground(request,short_name,account=None):
    output = {}
    group = Group.by_short_name_and_user(short_name, account)

    output['num_statuses'] = group.status_count()
    
    complete = not group.isUpdating()
      
    output['complete'] = complete
    
    if group.oldestStatus():
        output['oldest_date'] = group.oldestStatus().status_date()
    if group.latestStatus():
        output['latest_date'] = group.latestStatus().status_date()
    
    if account:
        output['api_calls'] = account.rate_remaining
    response = HttpResponse()
    response.write(simplejson.dumps(output))
    return response    

@wants_account
def Tweet(request,status_id,account=None):
    output = {}
    status = Status.by_id(status_id)
    if not status:
        status = collector.status(status_id,account)
    if status:
        encodeURLs(status, account)
        output['status'] = render_to_string('status.html', {'status':status})
        output['next_status'] = str(status.in_reply_to_status_id)
    else:
        output['status'] = '<li>The next tweet no longer exists</li>'
        output['next_status'] = str(None)
    
    if account:
        output['api_calls'] = account.rate_remaining
    response = HttpResponse()
    response.write(simplejson.dumps(output))
    return response 
     
def UserRedirect(request):
    screen_name = request.REQUEST.get('screen_name')
    return HttpResponseRedirect('/user/'+screen_name)