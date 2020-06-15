import mysql.connector
import os
import json

sell_ads = [1193986, 1194070, 1194076]
buy_ads = [1194095, 1194098, 1194149]

parameters_sell_1193986 = {
    'account' : 'Cryptostrat.co.uk',
    'chat_id' : -457290542,
    'ad_number' :1193986,
    'action' : 'SELL',
    'not_follow_list':  json.dumps(['Cryptostrat.co.uk', 'Topogetcrypto']),
    'minimum_trade_count': 100, 
    'minimum_max_amount': 100, 
    'maximum_min_amount': 1000000, 
    'minimum_margin': 200,
    'maximum_margin': 8,
    'undercut': 10,
    'max_minutes_since_active': 15,
    'is_bot_active' : 'True',
    'tele_bot_refresh_seconds' : 5,
    'ad_list_stream' : 'False',
    'ad_price' : 9000,
}

parameters_sell_1194070 = {
    'account' : 'Cryptostrat.co.uk',
    'chat_id' : -394864872,
    'ad_number' : 1194070,
    'action' : 'SELL',
    'not_follow_list':  json.dumps(['Cryptostrat.co.uk', 'Topogetcrypto']),
    'minimum_trade_count': 100, 
    'minimum_max_amount': 100, 
    'maximum_min_amount': 1000000, 
    'minimum_margin': 200,
    'maximum_margin': 8,
    'undercut': 10,
    'max_minutes_since_active': 15,
    'is_bot_active' : 'True',
    'tele_bot_refresh_seconds' : 5,
    'ad_list_stream' : 'False',
    'ad_price' : 9000,
}


parameters_sell_1194076 = {
    'account' : 'Cryptostrat.co.uk',
    'chat_id' : -443832414,
    'ad_number' : 1194076,
    'action' : 'SELL',
    'not_follow_list':  json.dumps(['Cryptostrat.co.uk', 'Topogetcrypto']),
    'minimum_trade_count': 100, 
    'minimum_max_amount': 100, 
    'maximum_min_amount': 1000000, 
    'minimum_margin': 200,
    'maximum_margin': 8,
    'undercut': 10,
    'max_minutes_since_active': 15,
    'is_bot_active' : 'True',
    'tele_bot_refresh_seconds' : 5,
    'ad_list_stream' : 'False',
    'ad_price' : 9000,
}


parameters_buy_1194095 = {
    'account' : 'Cryptostrat.co.uk',
    'chat_id' : -343491942,
    'ad_number' : 1194095,
    'action' : 'BUY',
    'not_follow_list':  json.dumps(['Cryptostrat.co.uk', 'Topogetcrypto']),
    'minimum_trade_count': 100, 
    'minimum_max_amount': 100, 
    'maximum_min_amount': 1000000, 
    'minimum_margin': 200,
    'maximum_margin': 8,
    'undercut': 10,
    'max_minutes_since_active': 15,
    'is_bot_active' : 'True',
    'tele_bot_refresh_seconds' : 5,
    'ad_list_stream' : 'False',
    'ad_price' : 9000,
}


parameters_buy_1194098 = {
    'account' : 'Cryptostrat.co.uk',
    'chat_id' : -486616574,
    'ad_number' : 1194098,
    'action' : 'BUY',
    'not_follow_list':  json.dumps(['Cryptostrat.co.uk', 'Topogetcrypto']),
    'minimum_trade_count': 100, 
    'minimum_max_amount': 100, 
    'maximum_min_amount': 1000000, 
    'minimum_margin': 200,
    'maximum_margin': 8,
    'undercut': 10,
    'max_minutes_since_active': 15,
    'is_bot_active' : 'True',
    'tele_bot_refresh_seconds' : 5,
    'ad_list_stream' : 'False',
    'ad_price' : 9000,
}


parameters_buy_1194149 = {
    'account' : 'Cryptostrat.co.uk',
    'chat_id' : -467354397,
    'ad_number' : 1194149,
    'action' : 'BUY',
    'not_follow_list':  json.dumps(['Cryptostrat.co.uk', 'Topogetcrypto']),
    'minimum_trade_count': 100, 
    'minimum_max_amount': 100, 
    'maximum_min_amount': 1000000, 
    'minimum_margin': 200,
    'maximum_margin': 8,
    'undercut': 10,
    'max_minutes_since_active': 15,
    'is_bot_active' : 'True',
    'tele_bot_refresh_seconds' : 5,
    'ad_list_stream' : 'False',
    'ad_price' : 9000,
}


initial_bots_parameters = [parameters_sell_1193986, parameters_sell_1194070, parameters_sell_1194076, parameters_buy_1194095, parameters_buy_1194098, parameters_buy_1194149]
mydb = mysql.connector.connect(
  host= os.environ.get('MYSQL_HOST'),
  user=os.environ.get('MYSQL_USERNAME'),
  passwd= os.environ.get('MYSQL_PASSWORD'),
  database = os.environ.get('MYSQL_DATABASE')
)

mysql_cursor = mydb.cursor()


def create_table(mysql_cursor):
    create_table = "CREATE TABLE price_bots (id INT AUTO_INCREMENT PRIMARY KEY"
    for i in initial_bots_parameters[0]:
        create_table += f", {i} VARCHAR(255)"
    create_table += ")"
    mysql_cursor.execute(create_table)



def insert_initial_bot_parameters(mysql_cursor):
    for parameters in initial_bots_parameters:
        insert_into_table_sql = "INSERT INTO price_bots ("
        number_of_columns = 0
        for i in parameters:
            insert_into_table_sql += f"{i}, "
            number_of_columns += 1
        insert_into_table_sql = insert_into_table_sql[:-2]
        insert_into_table_sql += ")"
        insert_into_table_sql += " Values ("
        while number_of_columns > 0:
            insert_into_table_sql += "%s, "
            number_of_columns -= 1
        insert_into_table_sql = insert_into_table_sql[:-2]
        insert_into_table_sql += ")"
        val = tuple(parameters[key] for key in parameters)
        mysql_cursor.execute(insert_into_table_sql, val)
    mydb.commit()


mysql_cursor.execute("DROP TABLE price_bots")
create_table(mysql_cursor)
insert_initial_bot_parameters(mysql_cursor)


#Add multiple, use chat_id and ad number
sql = f"SELECT * FROM price_bots WHERE chat_id ={str(-394864872)}"

mysql_cursor.execute(sql)
myresult = mysql_cursor.fetchall()[0]

parameterss = {
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
print(parameterss['not_follow_list'])

def update_parameters(parameters):
    update_row_sql = f"UPDATE price_bots SET " #address = 'Canyon 123' WHERE chat_id ={str(-394864872)}"
    for key, value in parameters.items():
        if key == 'not_follow_list':
            value = json.dumps(value)
        update_row_sql += f"{key} = '{value}', "
    update_row_sql = update_row_sql[:-2]
    update_row_sql += f" WHERE chat_id ={str(-394864872)}"
    mysql_cursor.execute(update_row_sql)
    mydb.commit()

#update_row(parameterss)
    #"UPDATE price_bots SET address = 'Canyon 123' WHERE address = 'Valley 345'"
#val = tuple(parameters[key] for key in parameters)
#print(x)



# ("chat_id VARCHAR(255), ad_number VARCHAR(255), action VARCHAR(255), not_follow_list TEXT, minimum_trade_count VARCHAR(255), minimum_max_amount VARCHAR(255), maximum_min_amount VARCHAR(255), minimum_margin VARCHAR(255), max_minutes_since_active VARCHAR(255), is_bot_active VARCHAR(255), tele_bot_refresh_seconds VARCHAR(255), ad_list_stream VARCHAR(255))")
# ("chat_id, ad_number, action, not_follow_list, minimum_trade_count, minimum_max_amount, maximum_min_amount, minimum_margin, max_minutes_since_active, is_bot_active, tele_bot_refresh_seconds, ad_list_stream) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
# def insert_default(mycursor):
#     sql = "INSERT INTO price_bots (chat_id, ad_number, action, not_follow_list, minimum_trade_count, minimum_max_amount, maximum_min_amount, minimum_margin, max_minutes_since_active, is_bot_active, tele_bot_refresh_seconds, ad_list_stream) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#     val = (
#         chat_id,
#         ad_number,
#         action,
#         not_follow_list,
#         parameters['minimum_trade_count'], 
#         parameters['minimum_max_amount'], 
#         parameters['maximum_min_amount'], 
#         parameters['minimum_margin'],
#         parameters['maximum_margin'],
#         parameters['undercut'],
#         parameters['max_minutes_since_active'],
#         parameters['is_bot_active'],
#         tele_bot_refresh_seconds,
#         ad_list_stream,
        
#     )
#     mycursor.execute(sql, val)

# insert_default(mycursor)


"""Use one telegram bot. Depending on chat id, load and change different mysql columns"""

# #create table
# mycursor.execute("CREATE TABLE price_bots (id INT AUTO_INCREMENT PRIMARY KEY, chat_id VARCHAR(255), ad_number VARCHAR(255), action VARCHAR(255), not_follow_list TEXT, minimum_trade_count VARCHAR(255), minimum_max_amount VARCHAR(255), maximum_min_amount VARCHAR(255), minimum_margin VARCHAR(255), max_minutes_since_active VARCHAR(255), is_bot_active VARCHAR(255), tele_bot_refresh_seconds VARCHAR(255), ad_list_stream VARCHAR(255))")
# #mycursor.execute("DROP TABLE price_bots")