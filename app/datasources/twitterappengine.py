'''Helper code for running python-twitter on top of Google App Engine'''

import time

from django.utils import simplejson
from google.appengine.api import memcache
from google.appengine.ext import db

class _DbCacheEntry(db.Model):
    value = db.BlobProperty(required=True)
    timestamp = db.DateTimeProperty(required=True, auto_now=True)

class DbCache(object):
    '''Simple cache on top of Google App Engine's datastore'''
    def Get(self, key):
        entry = _DbCacheEntry.get_by_key_name(key)
        if entry:
            return entry.value
        else:
            return None
  
    def Set(self, key, data):
        entry = _DbCacheEntry.get_by_key_name(key)
        if not entry:
            entry = _DbCacheEntry(
                key_name = key,
                value = data)
        else:
            entry.value = data
        entry.put()
  
    def GetCachedTime(self, key):
        entry = _DbCacheEntry.get_by_key_name(key)
        if entry:
            try:
              # All cached data must be valid JSON, and if we mistakenly cache
              # error response, we should ignore them
              data = simplejson.loads(entry.value)
              if isinstance(data, dict) and data.has_key('error'):
                return None
            except:
              return None
      
            return time.mktime(entry.timestamp.utctimetuple())
        else:
            return None
    
        return None

class MemcacheCache(object):
    '''Simple cache on top of Google App Engine's memcache service'''
    def Get(self, key):
        values = memcache.get(key)
        if values:
            return values[1]
        return None

    def Set(self, key, data):
        memcache.set(key, [time.time(), data])

    def GetCachedTime(self, key):
        values = memcache.get(key)
        if values:
            return values[0]
        return None
    