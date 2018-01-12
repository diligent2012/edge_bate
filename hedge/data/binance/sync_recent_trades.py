# coding=utf-8
# 获取最近的交易

import sys,os
sys.path.append("../../platform/")
sys.path.append("../../util/")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *
from db_util import insert_binance_recent_trades_data, find_btc_binance_recent_trades_data_newest_one
from account_util import get_account_list

# 订单操作的币种
JOIN_ORDER_SYMBOL = [
    'EOSBTC',
    'EOSETH',
    'ETHBTC'
]

# 获取最近的交易（最多500）
def get_recent_trades(symbol='EOSBTC'):
    account_list = get_account_list()
    account = account_list[0]
    client = Client(account['api_key'], account['api_secret'])
    recent_trades = client.get_recent_trades(symbol = symbol)
    return recent_trades



def get_new_one():
    newest_one = find_btc_binance_recent_trades_data_newest_one()
    return newest_one['data_price']

# 获取最近的交易（最多500）
def sync_recent_trades(symbol='EOSBTC'):
    recent_trades = get_recent_trades(symbol)
    sync_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    prev_price = get_new_one()

    for key,item in enumerate(recent_trades):
        change_rate = round( (float(item['price']) - prev_price) / prev_price, 4)
        prev_price = float(item['price'])
        isBuyerMaker = 0
        if (item['isBuyerMaker']):
            isBuyerMaker = 1
        isBestMatch = 0
        if (item['isBestMatch']):
            isBestMatch = 1
        insert_binance_recent_trades_data(isBuyerMaker, item['price'], item['qty'], item['time'], item['id'], isBestMatch, sync_time, change_rate)
        
# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    sync_recent_trades()

if __name__ == '__main__':
    main() 