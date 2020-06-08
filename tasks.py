from celery import Celery
import os
from telegram import process_commands
from lbc import ad_process

CELERY_BROKER_URL = os.environ.get('CLOUDAMQP_URL')

app = Celery('price_bot', backend='amqp', broker=CELERY_BROKER_URL)


timezone = 'Europe/London'


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
    'get-telegram-commands-every-30-seconds': {
        'task': 'tasks.process_telegram',
        'schedule': 10.0,
        'args': ()
    },
    # 'update-localbitcoins-sell-1193986': {
    #     'task': 'tasks.process_localbitcoins_CS_Sell_ad_1193986',
    #     'schedule': 5.0,
    #     'args': ()
    # },
    'update-localbitcoins-sell-1194070': {
        'task': 'tasks.process_localbitcoins_CS_Sell_ad_1194070',
        'schedule': 5.0,
        'args': ()
    },
    'update-localbitcoins-sell-1194076': {
        'task': 'tasks.process_localbitcoins_CS_Sell_ad_1194076',
        'schedule': 5.0,
        'args': ()
    },
    # 'update-localbitcoins-buy-1194095': {
    #     'task': 'tasks.process_localbitcoins_CS_Buy_ad_1194095',
    #     'schedule': 5.0,
    #     'args': ()
    # },
    'update-localbitcoins-buy-1194098': {
        'task': 'tasks.process_localbitcoins_CS_Buy_ad_1194098',
        'schedule': 5.0,
        'args': ()
    },
    'update-localbitcoins-sell-1194149': {
        'task': 'tasks.process_localbitcoins_CS_Buy_ad_1194149',
        'schedule': 5.0,
        'args': ()
    },
}
app.conf.timezone = 'Europe/London'