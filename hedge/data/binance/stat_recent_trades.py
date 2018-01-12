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


# 统计最近交易数据
def stat_recent_trades(symbol='EOSBTC'):
    
# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    stat_recent_trades()

if __name__ == '__main__':
    main() 