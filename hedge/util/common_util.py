# coding=utf-8


import sys  
sys.path.append("..")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *

from db_util import insert_btc_binance_order, find_btc_binance_order_record, update_btc_binance_order_up, find_btc_binance_order_sell_record, update_btc_binance_order
from binance_util import get_client, get_all_orders, get_recent_trades, get_klines, get_ticker, get_order_book
from account_util import get_account_list
from helper_util import id_generator


# 同步所有订单
def common_sync_all_order(client, account):
    #account_list = get_account_list()
    #for key,a_item in enumerate(account_list):
        #client = get_client(a_item['api_key'], a_item['api_secret'])
        
    #获取所有订单
    all_orders = get_all_orders(client, 'EOSBTC');
    # 如果不为空
    if all_orders:
        for key,item in enumerate(all_orders):
            
            sellClientOrderId = id_generator()
            data = {}
            data['sellClientOrderId'] = sellClientOrderId
            data['account'] = account #a_item['account']
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
                print "新纪录"
                insert_btc_binance_order(data)
            else:
                print "老纪录"
                update_btc_binance_order(data)
                #print btc_binance_order_record
                common_update_order_up(btc_binance_order_record)



# 更新订单的上下架状态
def common_update_order_up(data):
    orderId = data['orderId'] # 订单ID
    account = data['account'] # 当前账户
    side = data['side'] # 买OR卖
    status = data['status'] # 状态
    sellClientOrderId = data['sellClientOrderId'] #买入对应卖出的客户端ID
    origQty = float(data['origQty']) # 订单数量
    executedQty = float(data['executedQty']) # 订单已经卖出数量
   
    if (9 == int(data['is_auto'])): # 是否加入自动程序
        return

    # 查询是否有正在进行的订单
    is_up_exist = find_btc_binance_order_is_up(account)
    if (not is_up_exist):
        # 置为9,下架的交易条件
            # 买入订单状态为FILLED,有对应的卖出订单,状态也为FILLED.该笔买入订单下架
        # 置为1,上架的交易条件
            # 买入订单状态为FILLED,没有对应的卖出订单,该笔买入订单上架
        if ('BUY' == side and 'FILLED' == status):
            is_result = find_btc_binance_order_sell_record(account, sellClientOrderId)
            if is_result:
                print "第01种场景: 订单号 %s 置为 9" % orderId 
                update_btc_binance_order_up(orderId, 9)
            else:
                print "第02种场景: 订单号 %s 置为 1" % orderId 
                update_btc_binance_order_up(orderId, 1)
                
    # 查询是否有正在进行的订单
    is_up_exist = find_btc_binance_order_is_up(account)
    if (not is_up_exist):
        # 置为9,下架的交易条件
            # 卖出订单状态为FILLED,该笔卖出订单下架
        if ('SELL' == side and 'FILLED' == status):
            print "第03种场景: 订单号 %s 置为 9" % orderId 
            update_btc_binance_order_up(orderId, 9)

        # 置为1,上架的交易条件
            # 卖出订单状态为CANCELED, 并且卖出数量和已经卖出数量不一致的,卖出数量不为0.0, 该笔卖出订单上架
        if ('SELL' == side and 'CANCELED' == status and origQty > executedQty and 0.0 != executedQty):
            print "第04种场景: 订单号 %s 置为 1" % orderId 
            update_btc_binance_order_up(orderId, 1)


# 获取当前的最高价格, 通过最近交易数据获取
def common_get_curr_max_price_recent(client):
    recent_trades = get_recent_trades(client)
    max_price = 0.0
    for key,item in enumerate(recent_trades):
        if(0 == key):
            max_price = item['price']
        else:
            if(item['price'] > max_price):
                max_price = item['price']
    
    # 将当前最高价格提高百分比
    max_price = float(max_price) * float(1)
    return round(max_price,8)



# # 获取当前的最高价格，通过K线数据获取
# def common_get_curr_max_price_klines(client):
#     klines = get_klines(client)
#     max_price = 0.0
#     ratio_num = 5
#     for key,item in enumerate(klines):
#         if(key > len(klines) - ratio_num):
#             if(key == len(klines) - ratio_num):
#                 max_price = item[2]
#             else:
#                 if(item[2] > max_price):
#                     max_price = item[2]

#     max_price = float(max_price) * float(1)
#     return round(max_price,8)

# def common_get_curr_max_price_24(client):
#     max_price = 0.0
#     ticker =  get_ticker(client)
#     for key,item in enumerate(ticker):
#         if ('EOSBTC' == item['symbol']):
#             max_price = item['askPrice']

#     max_price = float(max_price) * float(1)
#     return round(max_price,8)


# def common_get_curr_min_price_24(client):
#     max_price = 0.0
#     ticker =  get_ticker(client)
#     for key,item in enumerate(ticker):
#         if ('EOSBTC' == item['symbol']):
#             max_price = item['askPrice']

#     max_price = float(max_price) * float(1)
#     return round(max_price,8)


def common_get_curr_min_price_recent(client):
    recent_trades = get_recent_trades(client)
    min_price = 0.0
    for key,item in enumerate(recent_trades):
        if(key  == len(recent_trades) - 1):
            min_price = item['price']
    
    # 将当前最低价格降低百分比
    min_price = float(min_price) * float(1)
    return round(min_price,8)


