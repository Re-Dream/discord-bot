import json
import redis
import urllib.parse
import os

def load_settings():
    with open('settings.json', 'r') as f:
        return json.load(f)

def load_redis():
    url = urllib.parse.urlparse(os.environ.get('REDIS_URL'))
    r = redis.Redis(host=url.hostname, port=url.port, password=url.password)
    return r