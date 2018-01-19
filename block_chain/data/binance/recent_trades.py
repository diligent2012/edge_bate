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


def get_new_one(symbol):
    try:
        newest_one = find_btc_binance_recent_trades_data_newest_one(symbol)
        if(newest_one):
            return newest_one['data_price']
    except Exception as e:
        send_exception(traceback.format_exc())
    return 0.0

  

def start_sync():
    try:
        symbols = []
        account_list = get_account_list()
        # 循环不同的账户
        for key,a_item in enumerate(account_list):
            client = Client(a_item['api_key'], a_item['api_secret'])
            binance_symbols = a_item['allow_symbol']
            # 循环不同的币种
            for key,s_item in enumerate(binance_symbols): 
                symbol = s_item['symbol']
                if(symbol not in symbols):
                    symbols.append(symbol)

        for key,symbol in enumerate(symbols): 
            recent_trades = client.get_recent_trades(symbol = symbol)
            sync_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            prev_price = get_new_one(symbol)

            for key,item in enumerate(recent_trades):
                if(0.0 == prev_price):
                    change_rate = prev_price
                else:
                    change_rate = round( (float(item['price']) - prev_price) / prev_price, 4)
                prev_price = float(item['price'])

                data_id = item['id']
                is_exit = find_binance_recent_trades_data(data_id)
                if(not is_exit):
                    insert_binance_recent_trades_data(item['isBuyerMaker'], item['price'], item['qty'], item['time'], item['id'], item['isBestMatch'], sync_time, change_rate, symbol)
    except Exception as e:
        send_exception(traceback.format_exc())
# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_sync()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    

if __name__ == '__main__':
    main() 