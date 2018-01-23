# coding=utf-8
# 获取最近的交易

import sys,os
sys.path.append(os.path.abspath("../../lib"))
sys.path.append(os.path.abspath("../../common"))
reload(sys)
sys.setdefaultencoding('utf-8')

from binance_lib.client import Client
from binance_lib.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_lib.enums import *

from setting import *
from db import *
from util import *
from helper import *



def get_recent_trade_max_min_price_by_trade_time_six(client, symbol, limit = 100):
    max_price = 0.0
    min_price = 0.0
    min_trade_time = 0
    max_trade_time = 0
    max_id = 0
    min_id = 0

    try:
        recent_trades = client.get_recent_trades(symbol = symbol)
        
        for key,item in enumerate(recent_trades):
            if(len(recent_trades) - limit <= key):
                #print item
                if (len(recent_trades) - limit == key):
                    max_price = item['price']
                    min_price = item['price']
                    max_trade_time = item['time']
                    min_trade_time = item['time']
                    max_id = item['id']
                    min_id = item['id']
                else:
                    if(item['price'] > max_price):
                        max_price = item['price']
                        max_trade_time = item['time']
                        max_id = item['id']

                    if(item['price'] <= min_price):
                        min_price = item['price']
                        min_trade_time = item['time']
                        min_id = item['id']

    except BinanceAPIException as e:
        send_exception(traceback.format_exc())
        
    return round(float(min_price),8), min_trade_time, min_id, round(float(max_price),8), max_trade_time, max_id


def start_sync():
    try:
        
        client = Client('p62jyg4zFVvp6uboW0TmmAt0pSyIylVTpAgaZDBY19QlHasfUAqebS695OasreVp', 
            'IXub9vH9BRbKgsaMVCqe27250xEGXDLTXbvG4osGU0IAt8XEj1FWgzWUneeCrXCC')
        symbols = ['EOSBTC']


        for key,symbol in enumerate(symbols): 
            min_price, min_trade_time, min_id, max_price, max_trade_time, max_id = get_recent_trade_max_min_price_by_trade_time_six(client, symbol, 100)
            rate = round((max_price - min_price)/min_price,4)
            pk_id = '%s-%s' % (min_id,max_id)
            is_exit = find_binance_recent_trades_data_rate(pk_id)
            if(not is_exit):
                insert_binance_recent_trades_data_rate(max_price, min_price, max_trade_time, min_trade_time, rate, symbol, pk_id)
            
    except Exception as e:
        send_exception(traceback.format_exc())
# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_sync()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    

if __name__ == '__main__':
    main() 