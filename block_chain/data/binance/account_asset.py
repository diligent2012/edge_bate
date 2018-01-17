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


def start_sync():
    join_stat = ['EOS','BTC']
    account_list = get_account_list()
    account_item = account_list[0]
    client = Client(account_item['api_key'], account_item['api_secret'])
    account = account_item['account']

    date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    account_assets = client.get_account()
    for key,item in enumerate(account_assets['balances']):
        if item['asset'] in join_stat:
            asset = item['asset']
            free = item['free']
            locked = item['locked']
            insert_btc_binance_asset(account, asset, free, locked, date)
# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_sync()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    

if __name__ == '__main__':
    main() 