from lbcapi import api
import json
import hmac
import time
import requests
import datetime
import hashlib
from prettytable import PrettyTable
import threading
import os



def main():
    tele_bot()
    lbc_bot()

def tele_bot():
    global parameters
    global is_bot_active
    global not_follow_list
    global tele_bot_refresh_seconds
    global ad_list_stream
    global chat_id
    telegram_commands = telegram.get_commands(telegram_allowed_users, telegram_allowed_chats)
    for command in telegram_commands:
        if command.instruction == 'status':
            bot_status = 'Inactive'
            if is_bot_active:
                bot_status = 'Active'
            message = f'*{account} {bot_type} Bot *_({bot_status})_:\nMinimum Trade Count: *{parameters.minimum_trade_count} trades*\nMinimum Max Amount: *{parameters.minimum_max_amount} GBP*\nMaximum Min Amount: *{parameters.maximum_min_amount} GBP*\nMinimum Margin: *{parameters.minimum_margin} GBP*\nMaximum Margin: *{parameters.maximum_margin}%*\nUndercut: *{parameters.undercut} GBP*\nMaximum Minutes since active: *{parameters.max_minutes_since_active} minutes*\n\nSpot Price: *{global_spot_price} GBP*\n{bot_type}ing at: *{global_best_price} GBP*\nMargin: *{round(abs(global_best_price-global_spot_price),2)} GBP / {round(100*abs(global_best_price-global_spot_price)/global_spot_price,2)}%*'
            telegram.send_message(command.chat_id, message)

        elif command.instruction == 'activate': #activates both buy and sell bot
            if is_bot_active:
                telegram.send_message(command.chat_id, f'{bot_type} Bot is already ACTIVATED.')
            else: 
                is_bot_active = True
                telegram.send_message(command.chat_id, f'{bot_type} Bot is now ACTIVE.')
                tele_bot_refresh_seconds = 10
        elif command.instruction == 'deactivate':
            if not is_bot_active:
                telegram.send_message(command.chat_id, f'{bot_type} Bot is already DEACTIVATED.')
            else:
                is_bot_active = False
                telegram.send_message(command.chat_id, f'{bot_type} Bot is now DEACTIVATED.')
                tele_bot_refresh_seconds = 15
        elif command.instruction == 'tradecount':
                command = telegram.parameters_check_int(command)
                if command!= None:
                    parameters.minimum_trade_count = command.parameters
                    telegram.send_message(command.chat_id, f'Minimum trade count changed to: {parameters.minimum_trade_count} trades')
        elif command.instruction == 'maxamount':
            command = telegram.parameters_check_int(command)
            if command!= None:
                    parameters.minimum_max_amount = command.parameters
                    telegram.send_message(command.chat_id, f'Minimum Max Amount changed to: {parameters.minimum_max_amount} GBP')
        elif command.instruction == 'minamount':
            command = telegram.parameters_check_int(command)
            if command!= None:
                    parameters.maximum_min_amount = command.parameters
                    telegram.send_message(command.chat_id, f'Maximum Min Amount changed to: {parameters.maximum_min_amount} GBP')
        elif command.instruction == 'margin':
            command = telegram.parameters_check_int(command)
            if command!= None:
                    parameters.minimum_margin = command.parameters
                    telegram.send_message(command.chat_id, f'Minimum Margin changed to: {parameters.minimum_margin} GBP')
        elif command.instruction == 'maxmargin':
            command = telegram.parameters_check_int(command)
            if command!= None:
                    parameters.maximum_margin = command.parameters
                    telegram.send_message(command.chat_id, f'Maximum Margin changed to: {parameters.maximum_margin} %')
        elif command.instruction == 'undercut':
            command = telegram.parameters_check_float(command)
            if command!= None:
                    parameters.undercut = command.parameters
                    if bot_type.lower() == 'sell':
                        sign = '-'
                    else:
                        sign = '+'
                    telegram.send_message(command.chat_id, f'Undercut changed to:  {sign}{parameters.undercut} GBP')
        elif command.instruction == 'ad_list':
            print(command.parameters)
            chat_id = command.chat_id
            if command!= None and command.parameters == None:
                telegram.send_message_html(command.chat_id, f'<pre>{list_of_ads}</pre>')
            elif command.parameters.lower() == 'on':
                ad_list_stream = 'on'
                telegram.send_message(command.chat_id, f'Ad list stream turned on!')
            elif command.parameters.lower() == 'off':
                ad_list_stream = 'off'
                telegram.send_message(command.chat_id, f'Ad list stream turned off!')
            else:
                telegram.send_message(command.chat_id, 'Invalid Parameters! Valid paramaters are ON and OFF.')
        elif command.instruction == 'get_nfl':
            message = print_format_NFL(not_follow_list)
            telegram.send_message(command.chat_id, f'Not Follow List: {message}')
        elif command.instruction == 'add_nfl':
            not_follow_list.append(command.parameters)
            message = print_format_NFL(not_follow_list)
            telegram.send_message(command.chat_id, f'Not Follow List: {message}')
        elif command.instruction == 'rem_nfl':
            try:
                not_follow_list.remove(command.parameters)
                message = print_format_NFL(not_follow_list)
                telegram.send_message(command.chat_id, f'Not Follow List: {message}')
            except ValueError:
                message = print_format_NFL(not_follow_list)
                telegram.send_message(command.chat_id, f'{command.parameters} was not found in Not Follow List.\n\nNot Follow List: {message}')
        elif command.instruction == 'minutes_since':
            command = telegram.parameters_check_int(command)
            if command!= None:
                    parameters.max_minutes_since_active = command.parameters
                    telegram.send_message(command.chat_id, f'Maximum Minutes since active changed to: {parameters.max_minutes_since_active} minutes')
        elif command.instruction == 'spot':
            spot_price = spot_price = get_btcaverage_gbp_last()
            telegram.send_message(command.chat_id, f'BitcoinAverage.com: {spot_price}GBP')
        else:
            telegram.send_message(command.chat_id, f'Error: Invalid Command!')
    threading.Timer(tele_bot_refresh_seconds, tele_bot, [], ).start()
def lbc_bot():
    global global_spot_price
    global global_best_price
    global list_of_ads
    #not_follow_list, sell_parameters, buy_parameters, is_sell_bot_active, is_buy_bot_active, bot_refresh_time
    if is_bot_active:
            spot_price = get_btcaverage_gbp_last()
            if bot_type.lower() == 'sell':
                ad_update = lbc.ad_process(parameters, spot_price, 'SELL', sell_ad_number)
            if bot_type.lower() == 'buy':
                ad_update = lbc.ad_process(parameters, spot_price, 'BUY', buy_ad_number)
            print(ad_update['table'])
            print(f'You are {bot_type.lower()}ing at: ', ad_update['price'])
            print('\nSpot price: ',spot_price)
            global_spot_price = spot_price
            global_best_price = ad_update['price']
            list_of_ads = ad_update['table'].get_string(fields=["Username", "Price (GBP)", 'Min (GBP)', 'Max (GBP)'])
            #list_of_ads = list_of_ads.get_html_string()
    print("bot is active: ", is_bot_active)
    #ad_process(not_follow_list, minimum_trade_count, minimum_max_amount, maximum_min_amount, minimum_margin, maxmimum_margin undercut, spot_price)
    print(f'\n\nminimum trades: {parameters.minimum_trade_count}    minimum max: {parameters.minimum_max_amount}       maximum min: {parameters.maximum_min_amount}   min margin: {parameters.minimum_margin}     max margin: {parameters.maximum_margin}%     undercut: {parameters.undercut}     minutes since: {parameters.max_minutes_since_active}')
    if ad_list_stream == 'on':
        telegram.send_message_html(chat_id, f'<pre>{list_of_ads}</pre>')
    threading.Timer(lbc_bot_refresh_seconds, lbc_bot, [], ).start()
    
class lbc:   
    #class notification:
        #def __init__(self, url, created_at, contact_id, read, message, notification_id):
    class ad:
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
    class ad_process_parameters:
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
        unprocessed_ad_list = lbc.get_data(f'https://localbitcoins.com/{buy_sell.lower()}-bitcoins-online/{currency}/.json')['ad_list']
        ad_list = []
        for ad in unprocessed_ad_list:
            ad = ad['data']
            #buy ads don't have low_risk bool that considers time since first purchase and other things
            if ad['trade_type'] == 'ONLINE_SELL':
                is_low_risk = None
            elif ad['trade_type'] == 'ONLINE_BUY':
                is_low_risk = ad['is_low_risk']
            ad_list.append(lbc.ad(ad['ad_id'],
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
                return lbc.conn_call(GET_POST, method, parameters, object_id)
        except:
            time.sleep(2)
            return lbc.conn_call(GET_POST, method, parameters, object_id)        
    def get_data(url): #does not require keys (gets public data to circumvent blocks by other brokers)
        try:
            data = requests.get(url)
            if data.status_code == 200:
                return data.json()['data']
            else:
                print('\n\n\n\nLocalbitcoin error. Retrying in 2 seconds!!!!!!')
                time.sleep(2)
                return lbc.get_data(url)
        except:
            time.sleep(1)
            return lbc.get_data(url)
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
        my_ad = lbc.conn_call('GET', 'ad-get',None, ad_id)
        current_price = my_ad.json()['data']['ad_list'][0]['data']['price_equation']
        if current_price != str(price):
            price_equation = str(price)
            parameters = {'price_equation': price_equation}
            lbc.conn_call('POST', 'ad-equation', parameters, ad_id)
    def ad_process(ad_process_parameters, spot_price, buy_sell, ad_number):
        if buy_sell.lower() == 'sell':   #convert buy_sell to get the ads list because for the broker selling the localbitcoins page is buying
            buy_sell = 'buy'
        elif buy_sell.lower() == 'buy':
            buy_sell = 'sell'
        ad_list = lbc.get_national_bank_ad_list(buy_sell,'GBP')
        filtered_data = lbc.filter_ad_list(ad_list, ad_process_parameters.not_follow_list, ad_process_parameters.minimum_trade_count, ad_process_parameters.minimum_max_amount, ad_process_parameters.maximum_min_amount, ad_process_parameters.max_minutes_since_active)
        best_price= lbc.get_best_price(filtered_data, ad_process_parameters.minimum_margin, ad_process_parameters.maximum_margin, ad_process_parameters.undercut, spot_price, buy_sell)
        lbc.ad_update(best_price, ad_number)
        table = PrettyTable()
        table.field_names = ['Username', 'Trades(+)','Price (GBP)', 'Min (GBP)', 'Max (GBP)', 'Since Active (m)']
        for ad in filtered_data:
            table.add_row([ad.username, round(ad.trade_count), ad.price,ad.min_amount, ad.max_amount, ad.last_seen_diff()])
        return {'table': table, 'price': best_price} 
# def get_btcaverage_gbp_last():
#     timestamp = int(time.time())
#     payload = '{}.{}'.format(timestamp, btc_average_public_key)
#     hex_hash = hmac.new(btc_average_secret_key.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()
#     signature = '{}.{}'.format(payload, hex_hash)
#     url = 'https://apiv2.bitcoinaverage.com/indices/global/ticker/BTCGBP'
#     headers = {'X-Signature': signature}
#     try:
#         result = (requests.get(url=url, headers=headers)).json()['last']
#     except TimeoutError:
#         return get_btcaverage_gbp_last()
#     return result
def get_btcaverage_gbp_last():
    try:
        latest_price = requests.get(url='https://www.cryptostrat.co.uk/reference_price/gbp').json()
    except:
        time.sleep(2)
        get_btcaverage_gbp_last()
    return latest_price
class telegram:
    def requests(GET_POST, method, parameters):
        if GET_POST.upper() == 'GET':
            if parameters == None:
                data = requests.get(f'https://api.telegram.org/bot{telegram_bot_token}/{method}')
            else:
                data = requests.get(f'https://api.telegram.org/bot{telegram_bot_token}/{method}', params=parameters)
        elif GET_POST.upper() == 'POST':
            data = requests.post(url = f'https://api.telegram.org/bot{telegram_bot_token}/{method}', params=parameters)
        else:
            return(print('Unsupported requests method. It needs to be GET or POST'))
        if data.status_code == 200:
            return data
        else:
            print('Error encountered in telegram requests')
            time.sleep(2)
            return telegram.requests(GET_POST, method, parameters)
    class user:
        def __init__(self, 
                     user_id,
                     username
                    ):
            self.id = user_id
            self.username = username
    class command:
        def __init__(self, 
                     from_id,
                     from_username,
                     chat_id,
                     date,
                     instruction,
                     parameters
                    ):
            self.from_id = from_id
            self.from_username = from_username
            self.chat_id = chat_id
            self.date = date
            self.instruction = instruction
            self.parameters = parameters
    def get_commands(allowed_users, allowed_chats):
        updates = telegram.requests('GET', 'getUpdates', None).json()
        if updates['ok'] == False:
            print('error getting telegram update')
            return get_updates()
        else:
            commands = []
            is_command = False
            updates = updates['result']
            last_update = None
            for update in updates:
                is_message = 'message' in update
                if is_message:
                    message = update['message']
                    try:
                        message_text = message['text']
                    except KeyError:
                        last_update = update['update_id']
                        telegram.requests('GET', 'getUpdates', {'offset': (last_update)+1}).json()
                        'breaking'
                        break
                    is_command = message_text.startswith('/')
                    if is_command:
                        text = message['text'][1:]
                        text = text.split(" ", 1)
                        instruction = text[0]
                        paramaters = None
                        if len(text) > 1:
                            paramaters = text[1]
                        command = telegram.command(message['from']['id'],
                                                   message['from']['username'],
                                                   message['chat']['id'],
                                                   message['date'],
                                                   text[0],
                                                   paramaters
                                                  )
                        #check allowed user usernames,id, and chat id.
                        user_allowed = telegram.is_user_allowed(command.from_id, command.from_username,allowed_users)
                        chat_allowed = telegram.is_chat_allowed(command.chat_id, allowed_chats)
                        if  user_allowed and chat_allowed:
                            commands.append(command)
                last_update = update['update_id']
            if last_update is not None:
                telegram.requests('GET', 'getUpdates', {'offset': (last_update)+1}).json()
            return commands
    def is_user_allowed(user_id, username, allowed_users):
        user_allowed = False
        for user in allowed_users:
            if user.username == username and user.id == user_id:
                user_allowed = True
        return user_allowed
    def is_chat_allowed(chat_id, allowed_chats):
        chat_allowed = False
        for chat in allowed_chats:
            if chat_id == chat:
                chat_allowed = True
        return chat_allowed
    
    def send_message(chat_id, text):
        telegram.requests('POST', 'sendMessage', {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'})
    def send_message_html(chat_id, text):
        telegram.requests('POST', 'sendMessage', {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})
    def parameters_check_int(command):
        try:
            command.parameters = int(command.parameters)
        except ValueError:
            telegram.send_message(command.chat_id, 'Error! Invalid parameters')
            return None
        except TypeError:
            telegram.send_message(command.chat_id, 'Error! Parameters required')
            return None
        return command
    def parameters_check_float(command):
        try:
            command.parameters = round(float(command.parameters),2)
        except ValueError:
            telegram.send_message(command.chat_id, 'Error! Invalid parameters')
            return None
        except TypeError:
            telegram.send_message(command.chat_id, 'Error! Parameters required')
            return None
        return command
def print_format_NFL(not_follow_list):
    message = ''
    for user in not_follow_list:
        if message != '':
            message = message + ', '
        if user != not_follow_list[0]:
            message = message + user
    if message == '':
        message = 'None'
    return message
#global variables for status return
global_spot_price = None
global_best_price = None
#ad_process(not_follow_list, minimum_trade_count, minimum_max_amount, maximum_min_amount, minimum_margin, maxmimum_margin undercut, spot_price)
is_bot_active = True
lbc_bot_refresh_seconds = 3
tele_bot_refresh_seconds = 3
not_follow_list = ['Cryptostrat.co.uk']
list_of_ads = []
ad_list_stream = 'off'
chat_id = 0
########################################################################################
bot_type = None
account = None
hmac_key = None
hmac_secret = None
conn = None
sell_ad_number = None
buy_ad_number = None
telegram_bot_token = None
telegram_allowed_chats = None
#LBC Params
strat_hmac_key = os.environ.get('LBC_HMAC_KEY')
strat_hmac_secret = os.environ.get('LBC_HMAC_SECRET')
topo_hmac_key = None
topo_hmac_secret = None
strat_sell_ad_number = 1193986 
strat_buy_ad_number = 1194095 
topo_buy_ad_number = 193132
parameters = lbc.ad_process_parameters(not_follow_list, 100, 100, 1000000, 200, 8, 10, 15)
#Telegram params
telegram_allowed_users = [telegram.user(188606593,'inmymem'),telegram.user(163483123,'Topogetcrypto')]
strat_sell_telegram_bot_token = os.environ.get('TELEGRAM_SELL_BOT_TOKEN')  #stratba25 CSsell
strat_buy_telegram_bot_token = os.environ.get('TELEGRAM_BUY_BOT_TOKEN') #stratba78 CSbuy
strat_sell_telegram_allowed_chats = [-330499521]
strat_buy_telegram_allowed_chats = [-333638319]

########################################################################
bot_type = 'Buy'
#bot_type = 'Sell'
account = 'Cryptostrat.co.uk'
hmac_key = strat_hmac_key
hmac_secret = strat_hmac_secret
if bot_type == 'Buy':
    buy_ad_number = strat_buy_ad_number
    telegram_bot_token = strat_buy_telegram_bot_token 
    telegram_allowed_chats = strat_buy_telegram_allowed_chats
if bot_type == 'Sell':
    sell_ad_number = strat_sell_ad_number
    telegram_bot_token = strat_sell_telegram_bot_token 
    telegram_allowed_chats = strat_sell_telegram_allowed_chats
conn = api.hmac(hmac_key, hmac_secret)
not_follow_list.remove(account)#put the account in the beginning so that it does not show up
not_follow_list.insert(0,account)




if __name__ == "__main__":
    main()

#Command list to send to botfather
#status - get bot parameters and status   
#activate - turn bot on
#deactivate - turn bot off
#tradecount - set minimum trade count
#maxamount - set minimum max amount
#minamount - set maximum min amount
#margin - set minimum margin
#maxmargin - set maximum margin (incase all others are offline)
#undercut - set undercut
#ad_list - get ad list of competition (Use parameters On and Off to switch stream) 
#get_nfl - get the Not Follow List 
#add_nfl - add member to Not Follow List 
#rem_nfl - remove member from Not Follow List
#minutes_since - set competitor maximum minutes since active
#spot - get bitcoinaverage.com spot price