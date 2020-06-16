from celery import Celery
import os
from telegram import process_commands
from lbc import ad_process
import datetime
from datetime import timedelta

CELERY_BROKER_URL = os.environ.get('REDISCLOUD_URL')

app = Celery('price_bot', broker=CELERY_BROKER_URL)

#app.conf.broker_transport_options = {'visibility_timeout': 60}  # 1 minute.
app.conf.broker_transport_options = {'fanout_prefix': True}
app.conf.broker_transport_options = {'fanout_patterns': True}
app.conf.result_expires = 15
app.conf.broker_pool_limit = 0
app.conf.enable_utc = True
app.conf.timezone = 'UTC'
#app.conf.broker_pool_limit = 20
app.conf.redis_max_connections = 90
#app.conf.worker_concurrency = 3
app.conf.worker_concurrency = 1
app.conf.worker_prefetch_multiplier = 1
# timezone = 'Europe/London'

sell_ads = [1193986, 1194070, 1194076]
buy_ads = [1194095, 1194098, 1194149]

@app.task
def process_telegram():
    process_commands()

@app.task
def process_localbitcoins_CS_Sell_ad_1193986():
    ad_process(1193986)
@app.task
def process_localbitcoins_CS_Sell_ad_1194070():
    ad_process(1194070)
@app.task
def process_localbitcoins_CS_Sell_ad_1194076():
    ad_process(1194076)


@app.task
def process_localbitcoins_CS_Buy_ad_1194095():
    ad_process(1194095)
@app.task
def process_localbitcoins_CS_Buy_ad_1194098():
    ad_process(1194098)
@app.task
def process_localbitcoins_CS_Buy_ad_1194149():
    ad_process(1194149)


app.conf.beat_schedule = {
    'get-telegram-commands-every-10-seconds': {
        'task': 'tasks.process_telegram',
        'schedule': 10.0,
        'args': (),
        # 'options': {
        #     'expires': datetime.datetime.utcnow() + datetime.timedelta(seconds=60),
        # }
    },
    'update-localbitcoins-sell-1193986': {
        'task': 'tasks.process_localbitcoins_CS_Sell_ad_1193986',
        'schedule': 3.0,
        'args': (),
        # 'options': {
        #     'expires': datetime.datetime.utcnow() + datetime.timedelta(seconds=45),
        # }
    },
    # 'update-localbitcoins-sell-1194070': {
    #     'task': 'tasks.process_localbitcoins_CS_Sell_ad_1194070',
    #     'schedule': 5.0,
    #     'args': (),
    #     # 'options': {
    #     #     'expires': datetime.datetime.utcnow() + datetime.timedelta(seconds=45),
    #     # }
    # },
    # 'update-localbitcoins-sell-1194076': {
    #     'task': 'tasks.process_localbitcoins_CS_Sell_ad_1194076',
    #     'schedule': 5.0,
    #     'args': (),
    #     # 'options': {
    #     #     'expires': datetime.datetime.utcnow() + datetime.timedelta(seconds=45),
    #     # }
    # },
    'update-localbitcoins-buy-1194095': {
        'task': 'tasks.process_localbitcoins_CS_Buy_ad_1194095',
        'schedule': 3.0,
        'args': (),
        # 'options': {
        #     'expires': datetime.datetime.utcnow() + datetime.timedelta(seconds=45),
        # }
    },
    # 'update-localbitcoins-buy-1194098': {
    #     'task': 'tasks.process_localbitcoins_CS_Buy_ad_1194098',
    #     'schedule': 5.0,
    #     'args': (),
    #     # 'options': {
    #     #     'expires': datetime.datetime.utcnow() + datetime.timedelta(seconds=45),
    #     # }
    # },
    # 'update-localbitcoins-sell-1194149': {
    #     'task': 'tasks.process_localbitcoins_CS_Buy_ad_1194149',
    #     'schedule': 5.0,
    #     'args': (),
    #     # 'options': {
    #     #     'expires': datetime.datetime.utcnow() + datetime.timedelta(seconds=45),
    #     # }
    # },
}
