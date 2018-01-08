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
from binance_util import get_recent_trades

# 订单操作的币种
JOIN_ORDER_SYMBOL = [
    'EOSBTC',
    'EOSETH',
    'ETHBTC'
]

# 获取最近的交易（最多500）
def sync_recent_trades(symbol='EOSBTC'):
    recent_trades = get_recent_trades(symbol)
    for key,item in enumerate(recent_trades):
        isBuyerMaker = 0
        if (item['isBuyerMaker']):
            isBuyerMaker = 1
        isBestMatch = 0
        if (item['isBestMatch']):
            isBestMatch = 1
        if(key == len(recent_trades) - 1):
            print item

        insert_binance_recent_trades_data(isBuyerMaker, item['price'], item['qty'], item['time'], item['id'], isBestMatch)

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    sync_recent_trades()

if __name__ == '__main__':
    main() 