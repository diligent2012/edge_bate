# coding=utf-8
# 获取24小时报价

import sys,os
sys.path.append("../../platform/")
sys.path.append("../../util/")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *

from db_util import *
from db_util import *
from binance_util import *
from account_util import *

def get_account_asset():

    join_stat = ['EOS','BTC']
    date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    account_list = get_account_list()

    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])
        account_config = a_item['account']
        account = get_account(client)
        for key,item in enumerate(account['balances']):
            if item['asset'] in join_stat:
                asset = item['asset']
                free = item['free']
                locked = item['locked']
                insert_btc_binance_asset(account_config, asset, free, locked, date)
   

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    get_account_asset()

if __name__ == '__main__':
    main() 