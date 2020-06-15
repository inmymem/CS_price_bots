from lbcapi import api
import mysql.connector
import os
import requests
import json
import datetime
import time
from prettytable import PrettyTable

hmac_key = os.environ.get('LBC_HMAC_KEY')
hmac_secret = os.environ.get('LBC_HMAC_SECRET')
conn = api.hmac(hmac_key, hmac_secret)

mysql_host = os.environ.get('MYSQL_HOST')
mysql_user = os.environ.get('MYSQL_USERNAME')
mysql_passwd= os.environ.get('MYSQL_PASSWORD')
mysql_database = os.environ.get('MYSQL_DATABASE')





class Ad:
    def __init__(self,
                    ad_id,
                    trade_type,
                    username,
                    feedback_score,
                    trade_count,
                    last_online,
                    price,
                    min_amount,
                    max_amount,
                    country_code,
                    currency,
                    online_provider,
                    require_feedback_score,
                    require_identification,
                    trusted_required,
                    sms_verification_required,
                    is_low_risk
                ):
        self.ad_id = ad_id
        self.trade_type = trade_type
        self.username = username
        self.feedback_score = feedback_score
        self.trade_count = float(trade_count.strip('+').replace(' ', '')) #remove the + and spaces in the trade count
        self.price = float(price)
        self.min_amount = min_amount #need to process it because max can be set to None
        self.min_amount = self.process_min_amount()
        self.max_amount = max_amount #need to process it because max can be set to None
        self.max_amount = self.process_max_amount()
        self.last_online = last_online
        self.country_code = country_code
        self.currency = currency
        self.online_provider = online_provider
        self.require_feedback_score = require_feedback_score
        self.require_identification = require_identification
        self.trusted_required = trusted_required
        self.sms_verification_required = sms_verification_required
        self.is_low_risk = is_low_risk
    def process_max_amount(self):
        if self.max_amount == None:
            max_amount = 100000000
        else:
            max_amount = float(self.max_amount)
        return max_amount
    def process_min_amount(self):
        if self.min_amount == None:
            min_amount = 0
        else:
            min_amount = float(self.min_amount)
        return min_amount
    def last_seen_diff(self):
        current_time = datetime.datetime.utcnow()
        difference = (current_time - self.last_online).total_seconds()/60
        return round(difference,2)


class Ad_Process_Parameters:
    def __init__(self,
                    not_follow_list, 
                    minimum_trade_count, 
                    minimum_max_amount, 
                    maximum_min_amount, 
                    minimum_margin,
                    maximum_margin,
                    undercut,
                    max_minutes_since_active):
        self.not_follow_list = not_follow_list 
        self.minimum_trade_count = minimum_trade_count
        self.minimum_max_amount = minimum_max_amount
        self.maximum_min_amount = maximum_min_amount
        self.minimum_margin = minimum_margin
        self.maximum_margin = maximum_margin
        self.undercut = undercut
        self.max_minutes_since_active = max_minutes_since_active


def get_national_bank_ad_list(buy_sell, currency):
    unprocessed_ad_list = get_data(f'https://localbitcoins.com/{buy_sell.lower()}-bitcoins-online/{currency}/.json')['ad_list']
    ad_list = []
    for ad in unprocessed_ad_list:
        ad = ad['data']
        #buy ads don't have low_risk bool that considers time since first purchase and other things
        if ad['trade_type'] == 'ONLINE_SELL':
            is_low_risk = None
        elif ad['trade_type'] == 'ONLINE_BUY':
            is_low_risk = ad['is_low_risk']
        ad_list.append(Ad(ad['ad_id'],
                                ad['trade_type'],
                                ad['profile']['username'],
                                ad['profile']['feedback_score'],
                                ad['profile']['trade_count'],
                                datetime.datetime.strptime(ad['profile']['last_online'], '%Y-%m-%dT%H:%M:%S+00:00'),
                                ad['temp_price'],
                                ad['min_amount'],
                                ad['max_amount_available'],
                                ad['countrycode'],
                                ad['currency'],
                                ad['online_provider'],
                                ad['require_feedback_score'],
                                ad['require_identification'],
                                ad['require_trusted_by_advertiser'],
                                ad['sms_verification_required'],
                                is_low_risk
                                )
                        )
    return ad_list


def filter_ad_list(ad_list, not_follow_list, minimum_trade_count, minimum_max_amount, maximum_min_amount, max_minutes_since_active):
    updated_ad_list = []
    maximum_last_seen_diff = max_minutes_since_active #maximum minutes since last seen
    for ad in ad_list:
        do_not_follow = False
        username = ad.username
        for username_to_not_follow in not_follow_list:
            if username_to_not_follow == username:
                do_not_follow = True
        if do_not_follow == False and ad.last_seen_diff() < maximum_last_seen_diff and ad.max_amount > minimum_max_amount and ad.min_amount < maximum_min_amount and ad.trade_count >= minimum_trade_count and (ad.is_low_risk == None or ad.is_low_risk == True) and ad.online_provider== 'NATIONAL_BANK':
            updated_ad_list.append(ad)
    return updated_ad_list


def conn_call(GET_POST, method, parameters, object_id):
    try: 
        if object_id == None and parameters == None:
            data = conn.call(GET_POST, f'/api/{method}/')
        elif object_id != None and parameters == None:
            data = conn.call(GET_POST, f'/api/{method}/{object_id}/')
        elif object_id == None and parameters != None:
            data = conn.call(GET_POST, f'/api/{method}/', params = parameters)
        else:
            data = conn.call(GET_POST, f'/api/{method}/{object_id}/', params = parameters)
        if data.status_code == 200:
            return data
        else:
            print('\n\n\n\nError encountered in localbitcoins requests. Retrying in 2 seconds!!!!!!')
            time.sleep(2)
            return conn_call(GET_POST, method, parameters, object_id)
    except:
        time.sleep(2)
        return conn_call(GET_POST, method, parameters, object_id)

        
def get_data(url): #does not require keys (gets public data to circumvent blocks by other brokers)
    try:
        data = requests.get(url)
        if data.status_code == 200:
            return data.json()['data']
        else:
            print('\n\n\n\nLocalbitcoin error. Retrying in 2 seconds!!!!!!')
            time.sleep(2)
            return get_data(url)
    except:
        time.sleep(1)
        return get_data(url)


def get_best_price(ad_list, minimum_margin, maximum_margin, undercut, spot_price, buy_sell):
    if buy_sell.lower() == 'buy':
        minimum_price = spot_price + minimum_margin
        if len(ad_list) == 0: #edge case if no one else is online
            return(spot_price * (1+maximum_margin/100 ))
        for ad in ad_list:
            best_competitor_price = ad.price
            best_price = best_competitor_price - undercut
            if best_price > minimum_price:
                break
            else:
                best_price = minimum_price
        return(best_price)
    if buy_sell.lower() == 'sell':
        maximum_price = spot_price - minimum_margin
        if len(ad_list) == 0: #edge case if no one else is online
            return(spot_price * (1-maximum_margin/100))
        for ad in ad_list:
            best_competitor_price = ad.price
            best_price = best_competitor_price + undercut
            if best_price < maximum_price:
                break
            else:
                best_price = maximum_price
        return(best_price)


def ad_update(price, ad_id):
    parameters = {'price_equation': price}
    conn_call('POST', 'ad-equation', parameters, ad_id)


def get_btcaverage_gbp_last():
    try:
        latest_price = requests.get(url='https://www.cryptostrat.co.uk/reference_price/gbp').json()
    except:
        time.sleep(2)
        get_btcaverage_gbp_last()
    return latest_price

def ad_process(ad_number):
    #get parameters by looking at ad_number
    mydb = mysql.connector.connect(
        host = mysql_host,
        user = mysql_user,
        passwd = mysql_passwd,
        database = mysql_database
        )
    mysql_cursor = mydb.cursor()
    sql = f"SELECT * FROM price_bots WHERE ad_number ={str(ad_number)}"
    mysql_cursor.execute(sql)
    myresult = mysql_cursor.fetchall()[0]
    parameters = {
            'account' : myresult[1],
            'chat_id' : myresult[2],
            'ad_number' : myresult[3],
            'action' : myresult[4],
            'not_follow_list':  json.loads(myresult[5]),
            'minimum_trade_count': float(myresult[6]), 
            'minimum_max_amount': float(myresult[7]), 
            'maximum_min_amount': float(myresult[8]), 
            'minimum_margin': float(myresult[9]),
            'maximum_margin': float(myresult[10]),
            'undercut': float(myresult[11]),
            'max_minutes_since_active': float(myresult[12]),
            'is_bot_active' : myresult[13],
            'tele_bot_refresh_seconds' : float(myresult[14]),
            'ad_list_stream' : myresult[15],
            'ad_price' : float(myresult[16]),
            }
    mysql_cursor.close()
    mydb.close()
    previous_price = parameters['ad_price']
    #print(f'previous ad priceee =  {previous_price}')
    if parameters['is_bot_active'] == 'True':
        spot_price = get_btcaverage_gbp_last()
        if parameters['action'].lower() == 'sell':   #convert buy_sell to get the ads list because for the broker selling the localbitcoins page is buying
            buy_sell = 'buy'
        elif parameters['action'].lower() == 'buy':
            buy_sell = 'sell'
        #print('start')
        ad_list = get_national_bank_ad_list(buy_sell,'GBP')
        #print('end')
        filtered_data = filter_ad_list(ad_list, parameters['not_follow_list'], parameters['minimum_trade_count'], parameters['minimum_max_amount'], parameters['maximum_min_amount'], parameters['max_minutes_since_active'])
        best_price= get_best_price(filtered_data, parameters['minimum_margin'], parameters['maximum_margin'], parameters['undercut'], spot_price, buy_sell)
        if best_price != previous_price:
            ad_update(best_price, ad_number)
        table = PrettyTable()
        table.field_names = ['Username', 'Trades(+)','Price (GBP)', 'Min (GBP)', 'Max (GBP)', 'Since Active (m)']
        for ad in filtered_data:
            table.add_row([ad.username, round(ad.trade_count), ad.price,ad.min_amount, ad.max_amount, ad.last_seen_diff()])
        update_row_sql = f"UPDATE price_bots SET ad_price = {best_price} WHERE ad_number ={str(ad_number)}"
        #print(table)
        #print(f'selling at {best_price}')
        #print(f'previous ad priceee =  {previous_price}')
        mydb = mysql.connector.connect(
            host = mysql_host,
            user = mysql_user,
            passwd = mysql_passwd,
            database = mysql_database
            )
        mysql_cursor = mydb.cursor()
        mysql_cursor.execute(update_row_sql)
        mydb.commit()
        mysql_cursor.close()
        mydb.close()
    #return {'table': table, 'price': best_price}