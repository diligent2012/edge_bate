# coding=utf-8


import sys  
sys.path.append("..")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *

from db_util import insert_btc_binance_order, find_btc_binance_order_record
from binance_util import get_client, get_all_orders
from account_util import get_account_list
from helper_util import id_generator


def common_sync_all_order():
    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])
        
        #获取所有订单
        all_orders = get_all_orders(client, 'EOSBTC');
        # 如果不为空
        if all_orders:
            for key,item in enumerate(all_orders):
                
                sellClientOrderId = id_generator()
                data = {}
                data['sellClientOrderId'] = sellClientOrderId
                data['account'] = a_item['account']
                data['orderId'] = item['orderId']
                data['clientOrderId'] = item['clientOrderId']
                data['origQty'] = item['origQty']
                data['icebergQty'] = item['icebergQty']
                data['symbol'] = item['symbol']
                data['side'] = item['side']
                data['timeInForce'] = item['timeInForce']
                data['status'] = item['status']
                data['stopPrice'] = item['stopPrice']
                data['time'] = item['time']
                data['isWorking'] = item['isWorking']
                data['o_type'] = item['type']
                data['price'] = item['price']
                data['executedQty'] = item['executedQty']
                btc_binance_order_record = find_btc_binance_order_record(item['orderId'])
                
                if not btc_binance_order_record:
                    print "有新纪录"
                    insert_btc_binance_order(data)



