import pickle
from redis import Redis
import subprocess
from uuid import uuid4

from app_config import SENTRY_DSN, REDIS_QUEUE_KEY

from raven import Client

sentry = Client(SENTRY_DSN)

redis = Redis()

class DelayedResult(object):
    def __init__(self, key):
        self.key = key
        self._rv = None

    @property
    def return_value(self):
        if self._rv is None:
            rv = redis.get(self.key)
            if rv is not None:
                self._rv = pickle.loads(rv)
        return self._rv

def queuefunc(f):
    def delay(*args, **kwargs):

        qkey = REDIS_QUEUE_KEY
        key = '%s:result:%s' % (qkey, str(uuid4()))
        s = pickle.dumps((f, key, args, kwargs))
        
        redis.rpush(REDIS_QUEUE_KEY, s)
        
        return DelayedResult(key)
    
    f.delay = delay
    return f

@queuefunc
def run_scripts(scripts, args):
    build, publish = scripts

    try:
        output = subprocess.check_output([build] + args)
        output = subprocess.check_output([publish] + args)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            sentry.captureException()
        else:
            pass

def queue_daemon():
    print('Listening for work ... ')
    while 1:
        msg = redis.blpop(REDIS_QUEUE_KEY)
        func, key, args, kwargs = pickle.loads(msg[1])
        
        try:
            rv = func(*args, **kwargs)
        except Exception as e:
            sentry.captureException()
            rv = e.message
        
        if rv is not None:
            redis.set(key, pickle.dumps(rv))
            redis.expire(key, rv_ttl)
