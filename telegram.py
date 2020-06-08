import requests
import os
import mysql.connector
import json
import time 
telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')

mysql_host = os.environ.get('MYSQL_HOST')
mysql_user = os.environ.get('MYSQL_USERNAME')
mysql_passwd= os.environ.get('MYSQL_PASSWORD')
mysql_database = os.environ.get('MYSQL_DATABASE')


def request(GET_POST, method, parameters):
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
        return request(GET_POST, method, parameters)


class User:
    def __init__(self, 
                    user_id,
                    username
                ):
        self.id = user_id
        self.username = username


class Command:
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
    updates = request('GET', 'getUpdates', None).json()
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
                    # request('GET', 'getUpdates', {'offset': (last_update)+1}).json()
                    # 'breaking'
                    break
                is_command = message_text.startswith('/')
                if is_command:
                    text = message['text'][1:]
                    text = text.split(" ", 1)
                    instruction = text[0]
                    paramaters = None
                    if len(text) > 1:
                        paramaters = text[1]
                    command = Command(message['from']['id'],
                                                message['from']['username'],
                                                message['chat']['id'],
                                                message['date'],
                                                text[0],
                                                paramaters
                                                )
                    #check allowed user usernames,id, and chat id.
                    user_allowed = is_user_allowed(command.from_id, command.from_username,allowed_users)
                    chat_allowed = is_chat_allowed(command.chat_id, allowed_chats)
                    if  user_allowed and chat_allowed:
                        commands.append(command)
            last_update = update['update_id']
        if last_update is not None:
            request('GET', 'getUpdates', {'offset': (last_update)+1}).json()
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
    request('POST', 'sendMessage', {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'})


def send_message_html(chat_id, text):
    request('POST', 'sendMessage', {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})


def parameters_check_int(command):
    try:
        command.parameters = int(command.parameters)
    except ValueError:
        send_message(command.chat_id, 'Error! Invalid parameters')
        return None
    except TypeError:
        send_message(command.chat_id, 'Error! Parameters required')
        return None
    return command


def parameters_check_float(command):
    try:
        command.parameters = round(float(command.parameters),2)
    except ValueError:
        send_message(command.chat_id, 'Error! Invalid parameters')
        return None
    except TypeError:
        send_message(command.chat_id, 'Error! Parameters required')
        return None
    return command


def get_btcaverage_gbp_last():
    try:
        latest_price = requests.get(url='https://www.cryptostrat.co.uk/reference_price/gbp').json()
    except:
        time.sleep(2)
        get_btcaverage_gbp_last()
    return latest_price

def update_parameters(parameters, mysql_cursor, mydb):
    update_row_sql = f"UPDATE price_bots SET " #address = 'Canyon 123' WHERE chat_id ={str(-394864872)}"
    for key, value in parameters.items():
        if key == 'not_follow_list':
            value = json.dumps(value)
        update_row_sql += f"{key} = '{value}', "
    update_row_sql = update_row_sql[:-2]
    update_row_sql += f" WHERE chat_id ={parameters['chat_id']}"
    mysql_cursor.execute(update_row_sql)
    mydb.commit()


def process_commands():
    #parameters, is_bot_active, not_follow_list, tele_bot_refresh_seconds, ad_list_stream, chat_id
    telegram_commands = get_commands(allowed_users, allowed_chats)
    
    if len(telegram_commands) > 0:
        mydb = mysql.connector.connect(
        host = mysql_host,
        user = mysql_user,
        passwd = mysql_passwd,
        database = mysql_database
        )
        mysql_cursor = mydb.cursor()

    #try str(parameters[command.chat_id])
    for command in telegram_commands:
        global_spot_price = get_btcaverage_gbp_last()
        sql = f"SELECT * FROM price_bots WHERE chat_id ={str(command.chat_id)}"
        mysql_cursor.execute(sql)
        myresult = mysql_cursor.fetchall()[0]
        parameters = {
            'account' : myresult[1],
            'chat_id' : myresult[2],
            'ad_number' : myresult[3],
            'action' : myresult[4],
            'not_follow_list':  json.loads(myresult[5]),
            'minimum_trade_count': myresult[6], 
            'minimum_max_amount': myresult[7], 
            'maximum_min_amount': myresult[8], 
            'minimum_margin': myresult[9],
            'maximum_margin': myresult[10],
            'undercut': myresult[11],
            'max_minutes_since_active': myresult[12],
            'is_bot_active' : myresult[13],
            'tele_bot_refresh_seconds' : myresult[14],
            'ad_list_stream' : myresult[15],
            'ad_price' : myresult[16],
            }
        global_best_price = float(parameters['ad_price'])
        if command.instruction == 'status':
            bot_status = 'Inactive'
            if parameters["is_bot_active"]:
                bot_status = 'Active'
            message = f'*{parameters["account"]} {parameters["action"]} Bot *_({bot_status})_:\nMinimum Trade Count: *{parameters["minimum_trade_count"]} trades*\nMinimum Max Amount: *{parameters["minimum_max_amount"]} GBP*\nMaximum Min Amount: *{parameters["maximum_min_amount"]} GBP*\nMinimum Margin: *{parameters["minimum_margin"]} GBP*\nMaximum Margin: *{parameters["maximum_margin"]}%*\nUndercut: *{parameters["undercut"]} GBP*\nMaximum Minutes since active: *{parameters["max_minutes_since_active"]} minutes*\n\nSpot Price: *{global_spot_price} GBP*\n{parameters["action"]}ing at: *{global_best_price} GBP*\nMargin: *{round(abs(global_best_price-global_spot_price),2)} GBP / {round(100*abs(global_best_price-global_spot_price)/global_spot_price,2)}%*'
            send_message(command.chat_id, message)
        elif command.instruction == 'activate': #activates both buy and sell bot
            if parameters["is_bot_active"] == 'True':
                send_message(command.chat_id, f'{parameters["action"]} Bot is already ACTIVATED.')
            else: 
                parameters["is_bot_active"] = 'True'
                send_message(command.chat_id, f'{parameters["action"]} Bot is now ACTIVE.')
                parameters["tele_bot_refresh_seconds"] = 10
        elif command.instruction == 'deactivate':
            if parameters["is_bot_active"] == 'False':
                send_message(command.chat_id, f'{parameters["action"]} Bot is already DEACTIVATED.')
            else:
                parameters["is_bot_active"] = 'False'
                send_message(command.chat_id, f'{parameters["action"]} Bot is now DEACTIVATED.')
                parameters["tele_bot_refresh_seconds"] = 15
        elif command.instruction == 'tradecount':
                command = parameters_check_int(command)
                if command!= None:
                    parameters['minimum_trade_count'] = command.parameters
                    send_message(command.chat_id, f'Minimum trade count changed to: {parameters["minimum_trade_count"]} trades')
        elif command.instruction == 'maxamount':
            command = parameters_check_int(command)
            if command!= None:
                    parameters['minimum_max_amount'] = command.parameters
                    send_message(command.chat_id, f'Minimum Max Amount changed to: {parameters["minimum_max_amount"]} GBP')
        elif command.instruction == 'minamount':
            command = parameters_check_int(command)
            if command!= None:
                    parameters['maximum_min_amount'] = command.parameters
                    send_message(command.chat_id, f'Maximum Min Amount changed to: {parameters["maximum_min_amount"]} GBP')
        elif command.instruction == 'margin':
            command = parameters_check_int(command)
            if command!= None:
                    parameters['minimum_margin'] = command.parameters
                    send_message(command.chat_id, f'Minimum Margin changed to: {parameters["minimum_margin"]} GBP')
        elif command.instruction == 'maxmargin':
            command = parameters_check_int(command)
            if command!= None:
                    parameters['maximum_margin'] = command.parameters
                    send_message(command.chat_id, f'Maximum Margin changed to: {parameters["maximum_margin"]} %')
        elif command.instruction == 'undercut':
            command = parameters_check_float(command)
            if command!= None:
                    parameters['undercut'] = command.parameters
                    if parameters["action"].lower() == 'sell':
                        sign = '-'
                    else:
                        sign = '+'
                    send_message(command.chat_id, f'Undercut changed to:  {sign}{parameters["undercut"]} GBP')
        elif command.instruction == 'ad_list':
            chat_id = command.chat_id
            if command!= None and command.parameters == None:
                send_message_html(command.chat_id, f'<pre>{list_of_ads}</pre>')
            elif command.parameters.lower() == 'on':
                parameters["ad_list_stream"] = True
                send_message(command.chat_id, f'Ad list stream turned on!')
            elif command.parameters.lower() == 'off':
                parameters["ad_list_stream"] = False
                send_message(command.chat_id, f'Ad list stream turned off!')
            else:
                send_message(command.chat_id, 'Invalid Parameters! Valid paramaters are ON and OFF.')
        elif command.instruction == 'get_nfl':
            message = print_format_NFL(parameters["not_follow_list"])
            send_message(command.chat_id, f'Not Follow List: {message}')
        elif command.instruction == 'add_nfl':
            parameters["not_follow_list"].append(command.parameters)
            message = print_format_NFL(parameters["not_follow_list"])
            send_message(command.chat_id, f'Not Follow List: {message}')
        elif command.instruction == 'rem_nfl':
            try:
                parameters["not_follow_list"].remove(command.parameters)
                message = print_format_NFL(parameters["not_follow_list"])
                send_message(command.chat_id, f'Not Follow List: {message}')
            except ValueError:
                message = print_format_NFL(parameters["not_follow_list"])
                send_message(command.chat_id, f'{command.parameters} was not found in Not Follow List.\n\nNot Follow List: {message}')
        elif command.instruction == 'minutes_since':
            command = parameters_check_int(command)
            if command!= None:
                    parameters['max_minutes_since_active'] = command.parameters
                    send_message(command.chat_id, f'Maximum Minutes since active changed to: {parameters["max_minutes_since_active"]} minutes')
        elif command.instruction == 'spot':
            spot_price = spot_price = get_btcaverage_gbp_last()
            send_message(command.chat_id, f'BitcoinAverage.com: {spot_price}GBP')
        else:
            send_message(command.chat_id, f'Error: Invalid Command!')
        update_parameters(parameters, mysql_cursor, mydb)


allowed_users = [User(188606593,'inmymem'), User(163483123,'Topogetcrypto')]
allowed_chats = [-394864872, -443832414, -486616574, -467354397] # -333638319

updates = request('GET', 'getUpdates', None).json()
print(updates)