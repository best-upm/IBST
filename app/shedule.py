"""import time
from redis import Redis
import rq
from rq import Queue
from rq_scheduler import Scheduler
from datetime import datetime
from app.shortcut.shortcut import delete_expired_links

from app import db
from app.models import *

scheduler=Scheduler('BOSS-tasks', connection=Redis.from_url('redis://'))
#function = delete_expired_objects(URL_Shortener())
scheduler.cron("0 0 * * * ", delete_expired_links)  #Min, Hour, Day, Week, Month

def example(seconds):
    print('Starting task')
    for i in range(seconds):
        print(i)
        time.sleep(1)
    print('Task completed')
"""
