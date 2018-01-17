# coding=utf-8


import sys,os
sys.path.append(os.path.abspath("../lib"))
sys.path.append(os.path.abspath("../common"))
from binance_lib.client import Client
from binance_lib.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_lib.enums import *
import traceback

from db import *
from util import *

# 同步所有订单
def sync_all_order(client, account, symbol, start_auto_date, oper_record_log):
    new_count = 0
    old_connt = 0
    #获取所有订单
    all_orders = client.get_all_orders(symbol = symbol);
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
                #print "新纪录"
                new_count += 1
                insert_btc_binance_order(data)
            else:
                #print "老纪录"
                old_connt += 1
                update_btc_binance_order(data)
                #print btc_binance_order_record
                common_update_order_up(btc_binance_order_record, start_auto_date)
    
    if (0 == old_connt and 0 == new_count):
        oper_record_log += "\n40-A、同步数据 账户: %s 币种: %s 没有数据" % (account, symbol)
    else:
        oper_record_log += "\n40-B、同步数据 账户: %s 币种: %s 新纪录数量: %s 老纪录数量: %s" % (account, symbol, new_count,old_connt)

    return oper_record_log


# 更新订单的上下架状态
def common_update_order_up(data, start_auto_date):
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
    is_up_exist = find_btc_binance_order_is_up(account, start_auto_date)
    if (not is_up_exist):
        # 置为9,下架的交易条件
            # 买入订单状态为FILLED,有对应的卖出订单,状态也为FILLED.该笔买入订单下架
        # 置为1,上架的交易条件
            # 买入订单状态为FILLED,没有对应的卖出订单,该笔买入订单上架
        if ('BUY' == side and 'FILLED' == status):
            is_result = find_btc_binance_order_sell_record(account, sellClientOrderId)
            if is_result:
                #print "第01种场景: 订单号 %s 置为 9" % orderId 
                update_btc_binance_order_up(orderId, 9)
            else:
                #print "第02种场景: 订单号 %s 置为 1" % orderId 
                update_btc_binance_order_up(orderId, 1)

    # 查询是否有正在进行的订单
    is_up_exist = find_btc_binance_order_is_up(account, start_auto_date)
    if (not is_up_exist):
        # 置为9,下架的交易条件
            # 卖出订单状态为FILLED,该笔卖出订单下架
        if ('SELL' == side and 'FILLED' == status):
            #print "第03种场景: 订单号 %s 置为 9" % orderId 
            update_btc_binance_order_up(orderId, 9)

        # 置为1,上架的交易条件
            # 卖出订单状态为CANCELED, 并且卖出数量和已经卖出数量不一致的,卖出数量不为0.0, 该笔卖出订单上架
        if ('SELL' == side and 'CANCELED' == status and origQty > executedQty and 0.0 != executedQty):
            #print "第04种场景: 订单号 %s 置为 1" % orderId 
            update_btc_binance_order_up(orderId, 1)

# 根据上一次交易时间,获取之后的最近交易记录中最高和最低价格
def get_recent_trade_max_min_price_by_trade_time(client, symbol, trade_time = 0):
    recent_trades = client.get_recent_trades(symbol = symbol)
    if (0 != trade_time) :
        filter_recent_trades = []
        for key,item in enumerate(recent_trades):
            if(item['time'] >= trade_time):
                filter_recent_trades.append(item)
        recent_trades = filter_recent_trades 


    max_price = 0.0
    min_price = 0.0
    for key,item in enumerate(recent_trades):
        if (0 == key):
            max_price = item['price']
            min_price = item['price']
        else:
            if(item['price'] > max_price):
                max_price = item['price']

            if(item['price'] <= min_price):
                min_price = item['price']
    
    return min_price, max_price

# 止损
def create_stop_sell_order(client, symbol, side, o_type, timeInForce, quantity, price, stopPrice, newClientOrderId ):
    try:
        create_order_result = client.create_order(symbol = symbol, side = side, type = o_type, timeInForce = timeInForce, quantity = quantity, price = price, stopPrice = stopPrice, newClientOrderId = newClientOrderId)
        return create_order_result
    except BinanceAPIException as e:
        send_exception(traceback.format_exc())
    return False


# 止盈
def create_stop_buy_order(client, symbol, side, o_type, timeInForce, quantity, price, stopPrice):
    try:
        create_order_result = client.create_order(symbol = symbol, side = side, type = o_type, timeInForce = timeInForce, quantity = quantity, price = price, stopPrice = stopPrice)
        return create_order_result
    except BinanceAPIException as e:
        send_exception(traceback.format_exc())
    return False
