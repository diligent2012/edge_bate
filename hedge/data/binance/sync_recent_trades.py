# coding=utf-8
# 获取最近的交易

import sys,os
sys.path.append("../../platform/")
sys.path.append("../../util/")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *
from db_util import insert_binance_recent_trades_data
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

# 获取最近的交易（最多500）
def sync_recent_trades(symbol='EOSBTC'):
    recent_trades = get_recent_trades(symbol)
    sync_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    for key,item in enumerate(recent_trades):
        isBuyerMaker = 0
        if (item['isBuyerMaker']):
            isBuyerMaker = 1
        isBestMatch = 0
        if (item['isBestMatch']):
            isBestMatch = 1
        insert_binance_recent_trades_data(isBuyerMaker, item['price'], item['qty'], item['time'], item['id'], isBestMatch, sync_time)

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    sync_recent_trades()

if __name__ == '__main__':
    main() 