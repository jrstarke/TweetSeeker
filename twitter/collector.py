import time
from twitter import utils
from twitter.models import Person, Status
import datetime
import logging
from twitter_explorer import settings
from django.db import IntegrityError

SEARCH_HOST = "api.twitter.com"

USER_TIMELINE = "/1/statuses/user_timeline.json"
USER_DETAILS = "/1/users/show.json"
USER_FRIENDS = "/1/statuses/friends.json"
STATUS_DETAILS = "/1/statuses/show/"

def getTupleValue(key,tuples):
    if tuples:
        for tuple in tuples:
            if tuple[0] == key:
                return tuple[1]
    return None    

def getResource(host,path,user,params):
    url = "https://" + host + path
    
    logging.debug(str(path) + str(params))
    count = 0
    while True:
        result, headers = utils.api(url, user.token(), 'GET', **params)
        if result is not None:
            break
        time.sleep(2**+count)
    
    if (getTupleValue('x-ratelimit-class',headers) == 'api_identified'):
        remaining = int(getTupleValue("x-ratelimit-remaining",headers))
        reset = int(getTupleValue("x-ratelimit-reset",headers))
        if remaining:
            user.rate_remaining = remaining
        if reset:
            user.rate_reset = reset
        user.update()
    
    return result

def user_details(screen_name, user, params = {}):
    params["screen_name"] = screen_name
    result = getResource(SEARCH_HOST, USER_DETAILS, user, params)
    return result  

def user_details_by_id(id, user, params = {}):
    params["user_id"] = id
    result = getResource(SEARCH_HOST, USER_DETAILS, user, params)
    return result  

def status(id,user):
    params = {}
    params["trim_user"] = 1
    s = getResource(SEARCH_HOST, STATUS_DETAILS + str(id) + ".json", user, params)
    if "error" in s:
        return None
    person = person_by_id(s['user']['id'],user)
    time_scheme = '%a %b %d %H:%M:%S +0000 %Y'
    aTime = datetime.datetime.strptime(s["created_at"], time_scheme)
    aStatus = Status.objects.get_or_create(status_id=s["id"], defaults={'person':person,
                                                   'in_reply_to_user_id':s["in_reply_to_user_id"],
                                                   'in_reply_to_status_id':s["in_reply_to_status_id"],
                                                   'text':s["text"],
                                                   'created_at':aTime})[0]
    return aStatus

def user_statuses(screen_name, user, params = {}):
    params["screen_name"] = screen_name
    params["trim_user"] = 1
    params["include_rts"] = 1
    
    params["count"] = settings.COLLECTOR_PAGESIZE

    result = getResource(SEARCH_HOST, USER_TIMELINE, user, params)
   
    return result  

def person(name,account):
    p = user_details(name,account)
    if "error" in p:
        return None
    person = Person.objects.get_or_create(user_id=p['id'], screen_name = p["screen_name"])[0]
    person_update(person,p,account)
        #memcache.Client().set('Person:'+name, person, time=86400)
    
    return person

def person_by_id(id,account):
    p = user_details_by_id(id,account)
    if "error" in p:
        return None
    person = Person.objects.get_or_create(user_id=p['id'], screen_name = p['screen_name'])[0]
    person_update(person,p,account)
    
    return person

def person_update(person,p,account):
    person.screen_name = p["screen_name"]
    person.name = p["name"]
    person.description = p["description"]
    person.location = p["location"]
    person.profile_image_url = p["profile_image_url"]
    person.following_count = p["friends_count"]
    person.followers_count = p["followers_count"]
    person.update()

def person_update_tweets(person,account):
    params = {}
    count = 0;
    if person.max_id:
        params["max_id"] = person.max_id
    if person.since_id:
        params["since_id"] = person.since_id    
    statuses = user_statuses(person.screen_name,account, params)
    time_scheme = '%a %b %d %H:%M:%S +0000 %Y'
    for status in statuses:
        aTime = datetime.datetime.strptime(status["created_at"], time_scheme)
        try:
            aStatus = Status.objects.create(status_id=status['id'],
                                                   person=person,
                                                   in_reply_to_user_id=status["in_reply_to_user_id"],
                                                   in_reply_to_status_id=status["in_reply_to_status_id"],
                                                   text=status["text"],
                                                   created_at=aTime
                                                   )
            count = count+1
        except IntegrityError:
            pass
    if len(statuses) > 0:
        person.max_id = statuses[-1]['id']-1
        if person.oldest_status_id is None or person.oldest_status_id > statuses[-1]['id']:
            person.oldest_status_id = statuses[-1]['id']
        if person.latest_status_id is None or person.latest_status_id < statuses[0]['id']:
            person.latest_status_id = statuses[0]['id']
        person.incStatusCount(count)
    person.last_updated = datetime.datetime.now()
    person.update()
    return len(statuses)    

