#!/usr/bin/python
#coding:utf-8
# 币安平台自动交易
# 高频买入、卖出集合在一起

import sys,os
sys.path.append(os.path.abspath("../../lib"))
sys.path.append(os.path.abspath("../../common"))
reload(sys)
sys.setdefaultencoding('utf-8')
from binance_lib.client import Client
from binance_lib.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_lib.enums import *
from decimal import *
import traceback

from setting import *
from db import *
from util import *
from helper import *

class BinanceClient(object):

    def __init__(self, api_key, api_secret):
        if not hasattr(BinanceClient, 'conn'):  
            BinanceClient.create_conn(api_key, api_secret)  
        self._connection = BinanceClient.conn
    
    @staticmethod  
    def create_conn(api_key, api_secret):  
        BinanceClient.conn = Client(api_key, api_secret)

    def get_conn(self):  
        return self._connection


# 开始同时买入和卖出
def start_same_auto_buy_sell():
    
    try:
        oper_record_log = "\nCommon-10、执行同时买卖开始" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        account_list = get_same_account_list()
        # 循环不同的账户
        for key,a_item in enumerate(account_list):

            
            client = BinanceClient(a_item['api_key'], a_item['api_secret']).get_conn()
            oper_record_log += "\nClient-10、重要实例化信息 : %s " % (str(client))
            oper_record_log += "\nClient-11、重要实例化信息 结束时间" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            time.sleep(1)
            account = a_item['account']
            qty = a_item['qty']
            start_auto_date = format_time_for_date(a_item['start_auto_date'])
            binance_symbols = a_item['allow_symbol']
            
            # 循环不同的币种
            for key,s_item in enumerate(binance_symbols): 
                symbol = s_item['symbol']
                
                oper_record_log += "\nCommon-20、账户: %s" % (account)
                oper_record_log += "\nCommon-30、币种: %s" % (symbol)
                                
                # 获取最新的订单
                oper_record_log += "\nCommon-40、获取最新的订单 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                is_ok, new_order, map_new_order, oper_record_log = get_newest_valid_order(client, account, symbol, oper_record_log)
                oper_record_log += "\n\nCommon-40-A、获取最新订单: 订单: %s 对应订单: %s " % (str(json.dumps(new_order)), str(json.dumps(map_new_order)))
                oper_record_log += "\nCommon-40、获取最新的订单 结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )



                side = 'same'

                # 如果正在进行订单,则继续进行
                if is_ok:
                    if new_order:
                        if map_new_order:

                            # 如果是卖出的话.降低 50%
                            if (SIDE_SELL == new_order['side']):
                                oper_record_log += "\nCommon-60、重新设置卖出 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                                oper_record_log += "\nCommon-60-A、没有及时卖出的订单: %s 当前买卖状态: %s" % (str(json.dumps(new_order)), str(new_order['side']))
                                orderId = new_order['orderId']
                                sell_price = round(float(new_order['price']),8) # 上一次卖出的价格
                                sell_time = new_order['time'] # 上一次卖出的时间
                                clientOrderId = new_order['clientOrderId'] 
                                buy_price = round(float(map_new_order['price']),8) # 买入的价格

                                oper_record_log += "\nCommon-60-B、重新设置卖出 的参数 订单ID: %s 卖出价格: %s 卖出时间: %s 客户端ID: %s 对应的买入价格: %s " % ( orderId, sell_price, sell_time, clientOrderId, buy_price)
                                oper_record_log = reset_auto_sell(client, account, orderId, sell_price, sell_time, symbol, qty, buy_price, clientOrderId, oper_record_log)
                                oper_record_log += "\n\nCommon-60、重新设置卖出 结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )

                            # 如果是买入的话.增加 50%
                            if (SIDE_BUY == new_order['side']):
                                oper_record_log += "\nCommon-70、重新设置买入 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                                oper_record_log += "\nCommon-7o-A、没有及时买入的订单: %s 当前买卖状态: %s" % (str(json.dumps(new_order)), str(new_order['side']))
                                orderId = new_order['orderId']
                                buy_price = round(float(new_order['price']),8) #上一次买入的价格
                                buy_time = new_order['time'] # 上一次卖出的时间
                                clientOrderId = new_order['clientOrderId'] 
                                sell_price = round(float(map_new_order['price']),8) # 卖出的价格
                                oper_record_log += "\nCommon-70-B、重新设置买入 的参数 订单ID: %s 买入价格: %s 买入时间: %s 客户端ID: %s 对应的卖出价格: %s" % ( orderId, buy_price, buy_time, clientOrderId, sell_price)
                                oper_record_log = reset_auto_buy(client, account, orderId, buy_price, buy_time, symbol, qty, sell_price, clientOrderId, oper_record_log)
                                oper_record_log += "\n\nCommon-70、重新设置买入 结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                        else:
                            oper_record_log += "\nCommon-80、进行中的订单没有对应的订单, 请注意: 订单: %s 对应订单: %s " % (str(json.dumps(new_order)), str(json.dumps(map_new_order)))
                        
                    else:
                        # 同时设定买入和卖出
                        oper_record_log += "\n\nCommon-90 同时设定买入和卖出订单 开始: %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                        oper_record_log = same_auto_buy_sell(client, account, symbol, qty, oper_record_log)
                        oper_record_log += "\n\nCommon-90 同时设定买入和卖出订单 结束: %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )

                oper_record_log += "\n\nCommon-99、执行同时买卖结束 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                insert_btc_binance_order_auto_log(account, side, symbol, oper_record_log)
    except Exception as e:
        send_exception(traceback.format_exc())

def reset_buy_rate_price(buy_price):
    buy_price = round( Decimal(buy_price) * (Decimal(1) + Decimal(0.0021)), 8)
    return buy_price

def reset_sell_rate_price(sell_price):
    sell_price = round( Decimal(sell_price) * (Decimal(1) - Decimal(0.0021)), 8)
    return sell_price

# 重新设置卖出
def reset_auto_sell(client, account, orderId, sell_price, sell_time, symbol, qty, buy_price, clientOrderId, oper_record_log):

    oper_record_log += "\n\nReset-Sell-01-A、手续费验证: 买入价格: %s " % (str(buy_price))
    buy_price = reset_buy_rate_price(buy_price)
    oper_record_log += "\nReset-Sell-01-B、手续费验证: 买入价格: %s " % (str(buy_price))

    # 降低卖出价格 = 卖出价格 -（卖出价格 - 加利润买入价格)/2
    new_sell_price = round( Decimal(sell_price) - ((Decimal(sell_price) - Decimal(buy_price)) / Decimal(2)), 8)
    #new_sell_price = round( Decimal(sell_price)  * (Decimal(1) - Decimal(0.001) * Decimal(0.8)), 8)

    if (buy_price > new_sell_price):
        oper_record_log += "\nReset-Sell-10、新的卖出价格 低于 对应的买入价格 不操作: 新的卖出价格: %s 买入价格: %s 新的币种: %s 新的数量: %s 客户端ID %s" % (str(new_sell_price), str(buy_price), str(symbol), str(qty), str(clientOrderId))
        return oper_record_log

    # 如果时间超过一分钟,就用当初买入价格加上手续费卖出
    # curr_time = int(round(time.time() * 1000))
    # diff_time = sell_time - curr_time
    # if diff_time > 1000 * 60:
    #     new_sell_price = buy_price
    #     oper_record_log += "\nReset-Sell-10-B、卖出的时间较长, 用买入价格加上手续费快速卖出: 相差时间: %s 上次卖出时间: %s 当前时间: %s 新的卖出价格: %s 买入价格: %s 新的币种: %s 新的数量: %s 客户端ID %s" % (str(diff_time), str(sell_time), str(curr_time), str(new_sell_price), str(buy_price), str(symbol), str(qty), str(clientOrderId))

    sellClientOrderId = clientOrderId.split('777')[0]
    sellClientOrderId = '%s%s%s' % (sellClientOrderId,'777',str(int(time.time())))

    oper_record_log += "\nReset-Sell-20、重新设置卖出订单信息: 新的卖出价格: %s 买入价格: %s 新的币种: %s 新的数量: %s 新的客户端ID %s" % (str(new_sell_price), str(buy_price), str(symbol), str(qty), str(sellClientOrderId))

    is_sell_cancel = cancel_order(client, symbol, orderId)
    if is_sell_cancel:
        sell_order_result = create_limit_sell_order(client, symbol, qty, new_sell_price, sellClientOrderId)
        oper_record_log += "\nReset-Sell-30、重新设置卖出 限价单返回: %s " % (str(json.dumps(sell_order_result)))
        if sell_order_result:
            insert_btc_binance_order_limit_buy_sell_record(sell_order_result, sellClientOrderId, account)
    else:
        oper_record_log += "\nReset-Sell-40、重新设置卖出前 取消订单失败: %s " % (str(json.dumps(is_sell_cancel)))

    return oper_record_log

# 重新设置买入
def reset_auto_buy(client, account, orderId, buy_price, buy_time, symbol, qty, sell_price, clientOrderId, oper_record_log):
    
    oper_record_log += "\n\nReset-Buy-01-A、手续费验证: 卖出价格: %s" % (str(sell_price))
    sell_price = reset_sell_rate_price(sell_price)
    oper_record_log += "\nReset-Buy-01-B、手续费验证: 卖出价格: %s" % (str(sell_price))

    # 提升买入价格 = 买入价格 + (加利润卖出价格 - 买入价格)/2
    new_buy_price = round( Decimal(buy_price) + ((Decimal(sell_price) - Decimal(buy_price)) / Decimal(2)), 8)
    #new_buy_price = round( Decimal(buy_price)  * (Decimal(1) + Decimal(0.001) * Decimal(0.8)), 8)

    if (sell_price < new_buy_price):
        oper_record_log += "\nReset-Buy-10、新的买入价格 高于 对应的卖出价格, 不操作: 新的买入价格: %s 卖出价格: %s 新的币种: %s 新的数量: %s " % (str(new_buy_price), str(sell_price), str(symbol), str(qty))
        return oper_record_log
    
    # 如果时间超过一分钟,就用当初买入价格加上手续费卖出
    # curr_time = int(round(time.time() * 1000))
    # diff_time = buy_time - curr_time
    # if diff_time > 1000 * 60:
    #     new_buy_price = sell_price
    #     oper_record_log += "\nReset-Buy-10、买入的时间较长, 用卖出价格减去手续费快速买入: 相差时间: %s 上次买入时间: %s 当前时间: %s 新的买入价格: %s 卖出价格: %s 新的币种: %s 新的数量: %s " % (str(diff_time), str(buy_time), str(curr_time), str(new_buy_price), str(sell_price), str(symbol), str(qty))

    #buyClientOrderId = id_generator()

    buyClientOrderId = clientOrderId.split('666')[0]
    buyClientOrderId = '%s%s%s' % (buyClientOrderId,'666',str(int(time.time())))

    oper_record_log += "\nReset-Buy-20、重新设置 买入订单信息: 新的买入价格: %s 卖出价格: %s 新的币种: %s 新的数量: %s 新的客户端ID %s" % (str(new_buy_price), str(sell_price), str(symbol), str(qty), str(buyClientOrderId))

    is_buy_cancel = cancel_order(client, symbol, orderId)
    if is_buy_cancel:
        buy_order_result = create_limit_buy_order(client, symbol, qty, new_buy_price, buyClientOrderId)
        oper_record_log += "\nBuy-Set-30、重新设置买入 设置限价单返回: %s " % (str(json.dumps(buy_order_result)))
        if buy_order_result:
            insert_btc_binance_order_limit_buy_sell_record(buy_order_result, 0, account)
    else:
        oper_record_log += "\nReset-Buy-40、重新设置买入前 取消订单失败: %s " % (str(json.dumps(is_buy_cancel)))

    return oper_record_log


#----------------------------------------------------下面是买入-------------------------------------------------------

def same_auto_buy_sell(client, account, symbol, qty, oper_record_log):
    # 获取当前最近的的交易中最高和最低价格
    oper_record_log += "\n\nBuySell-10、获取最高最低价格 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
    min_price, max_price = get_recent_trade_max_min_price_by_trade_time_limit(client, symbol, 100)
    oper_record_log += "\nBuySell-10-1、当前最高价格: %s 当前最低价格: %s " % (str(max_price), str(min_price))
    oper_record_log += "\nBuySell-20、获取最高最低价格  结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )

    # 判断是否有利润,并且获取买入价格、卖出价格
    is_allow_buy_sell, buy_price, sell_price, confirm_rate, rate, ref_rate = oper_same_buy_sell_price(min_price, max_price)
    oper_record_log += "\nBuySell-30、是否有利润: %s 确认利润率: %s 最初利润率: %s 参考利润率: %s 卖出价格: %s 买入价格: %s" % (str(is_allow_buy_sell), str(confirm_rate), str(rate), str(ref_rate), str(sell_price), str(buy_price))

    if is_allow_buy_sell:

        buy_price = round(buy_price, 8)
        sell_price = round(sell_price, 8)

        # 卖出价格 必须 大于 买入价格。兜底做法(以防意外)
        is_secure = same_buy_sell_secure_check(buy_price, sell_price)
        oper_record_log += "\nBuySell-50、是否安全: %s 买入价格: %s 卖出价格: %s" % (str(is_secure), str(buy_price), str(sell_price))
        if is_secure:
            # 设置买入
            oper_record_log = set_same_limit_buy_sell_price(client, account, buy_price, sell_price, qty, symbol, oper_record_log)
            sync_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            insert_binance_recent_trades_data_rate_test(account, buy_price, min_price, sell_price, max_price, qty, symbol, rate, confirm_rate, sync_time)
            send_wechat("开始同时买入和卖出了")

    return oper_record_log

# 卖出价格 必须 大于 买入价格。兜底做法(以防意外)
def same_buy_sell_secure_check(buy_price, sell_price):
    if(buy_price < sell_price):
        return True
    return False

# 判断是否有利润,并且获取买入价格、卖出价格
def oper_same_buy_sell_price(min_price, max_price):
        
    # 买入价格偏移幅度(上调)
    buy_price_offset = 0.55
    # 卖出价格偏移幅度(下调)
    sell_price_offset = 0.45

    # 固定利润比
    profit_rate = 0.003

    # 最高价格 和 最低价格的偏差幅度
    rate = 0.0

    # 参考利润比
    ref_rate = 0.004
    try:

        rate = round((max_price - min_price)/min_price,4)

        if(rate >= ref_rate):
            free_rate = rate - profit_rate

            buy_price = (1 + free_rate * buy_price_offset) * min_price

            sell_price = max_price / ((free_rate * sell_price_offset) + 1 ) 
            
            confirm_rate = round( (sell_price - buy_price) / buy_price, 4)
            if(confirm_rate >= profit_rate):
                return True, buy_price, sell_price, confirm_rate, rate, ref_rate
    except Exception as e:
        send_exception(traceback.format_exc())
    return False, 0.0, 0.0, 0.0, rate, ref_rate

# 开始设置买入和卖出限价单
def set_same_limit_buy_sell_price(client, account, buy_price,  sell_price, qty, symbol, oper_record_log):
    try:
        order_symbol = symbol
        order_type = ORDER_TYPE_LIMIT
        order_price = buy_price  # 买入价格
        order_quantity = qty

        buyClientOrderIdOri = id_generator()

        buyClientOrderId = '%s%s%s' % (buyClientOrderIdOri, '666', str(int(time.time())))
        # 设置限价单 限价价格、数量、币种
        oper_record_log += "\nBuy-Set-40、设置买入限价单 设置币种: %s 设置交易数量: %s 设置交易价格: %s  客户端ID: %s" % (order_symbol, order_quantity, order_price, buyClientOrderId)
        buy_order_result = create_limit_buy_order(client, order_symbol, order_quantity, order_price, buyClientOrderId)
        oper_record_log += "\nBuy-Set-49、设置限价单返回: %s " % (str(json.dumps(buy_order_result)))
        
        # 买入成功后,才设置卖出
        if buy_order_result:

            order_symbol = symbol
            order_type = ORDER_TYPE_LIMIT
            order_price = sell_price  # 卖出价格
            order_quantity = qty
            sellClientOrderId = '%s%s%s' % (buyClientOrderIdOri, '777', str(int(time.time())))
           
            # 设置限价单
            oper_record_log += "\nSell-Set-50、设置卖出限价单 设置币种: %s 设置交易数量: %s 设置交易价格: %s 客户端ID: %s" % (order_symbol, order_quantity, order_price, sellClientOrderId)
            sell_order_result = create_limit_sell_order(client, order_symbol, order_quantity, order_price, sellClientOrderId)
            oper_record_log += "\nSell-Set-59、设置卖出限价单返回: %s " % (str(json.dumps(sell_order_result)))
            if sell_order_result:
                oper_record_log += "\nSell-Set-88、买入卖出都设置成功 买入设置返回:%s 卖出设置返回:%s " % (str(json.dumps(buy_order_result)), str(json.dumps(sell_order_result)))
                # 买入成功和卖出成功 才插入数据库
                insert_btc_binance_order_limit_buy_sell_record(buy_order_result, 0, account)
                insert_btc_binance_order_limit_buy_sell_record(sell_order_result, buyClientOrderId, account)
            else:
                oper_record_log += "\nSell-Set-90、买入成功: %s ,但是卖出失败: %s " % (str(json.dumps(buy_order_result)), str(sell_order_result))
        else:
            oper_record_log += "\nSell-Set-91、买入失败,也就没有进行卖出: %s " % (str(buy_order_result))
    except Exception as e:
        send_exception(traceback.format_exc())
    finally:
        return oper_record_log
    return oper_record_log

#----------------------------------------------------下面是公共部分-------------------------------------------------------


def get_recent_trade_max_min_price_by_trade_time_limit(client, symbol, limit = 100):
    max_price = 0.0
    min_price = 0.0

    try:
        recent_trades = client.get_recent_trades(symbol = symbol)
        
        for key,item in enumerate(recent_trades):
            if(len(recent_trades) - limit <= key):
                
                if (len(recent_trades) - limit == key):
                    max_price = item['price']
                    min_price = item['price']
                else:
                    if(item['price'] > max_price):
                        max_price = item['price']

                    if(item['price'] <= min_price):
                        min_price = item['price']

    except BinanceAPIException as e:
        send_exception(traceback.format_exc())
        
    return round(float(min_price),8), round(float(max_price),8)

# 获取最新订单 code: Filled-*
def get_newest_valid_order(client, account, symbol, oper_record_log):

    buy_new_order = []
    sell_new_order = []

    buy_clientOrderId = ''
    sell_clientOrderId = ''

    new_order_item = {}
    map_new_order_item = {}

    is_partially_filled = False

    try:
        all_orders = client.get_all_orders(symbol = symbol);

        for key,item in enumerate(all_orders):

            if item['status'] == ORDER_STATUS_PARTIALLY_FILLED:
                is_partially_filled = True

            if item['status'] == ORDER_STATUS_NEW and item['type'] == 'LIMIT':
                if item['side'] == SIDE_BUY:
                    buy_new_order.append(item)
                    buy_clientOrderId = item['clientOrderId']

                if item['side'] == SIDE_SELL:
                    sell_new_order.append(item)
                    sell_clientOrderId = item['clientOrderId']


        if is_partially_filled:
            oper_record_log += "\n\nFilled-10、有订单部分买入或卖出,不能重设 账户: %s 币种: %s" % (str(account), str(symbol))
            return False, False, False, oper_record_log

        if not buy_new_order and not sell_new_order:
            oper_record_log += "\n\nFilled-20、没有订单进行中 账户: %s 币种: %s" % (str(account), str(symbol))
            return True, False, False, oper_record_log

        elif len(buy_new_order) > 1 or len(sell_new_order) > 1:
            oper_record_log += "\n\nFilled-30、有多个买入或者卖出的订单都在进行中: 买入订单: %s " % (str(json.dumps(buy_new_order)), str(json.dumps(sell_new_order)))
            return False, False, False, oper_record_log
        else:
            if buy_new_order and sell_new_order:
                oper_record_log += "\n\nFilled-40、非对应的买卖两单子都在进行中: 买入订单: %s 卖出订单: %s" % (str(json.dumps(buy_new_order)), str(json.dumps(sell_new_order)))
                return False, False, False, oper_record_log

            elif buy_new_order and not sell_new_order:
                new_order_item = buy_new_order[0]
                oper_record_log += "\n\nFilled-50、正在进行的买入订单: %s 当前状态: %s" % (str(json.dumps(new_order_item)), str(new_order_item['side']))
                
                map_new_order_item, oper_record_log = get_map_sell_order_item(all_orders, new_order_item, oper_record_log)
                if map_new_order_item:
                    return True, new_order_item, map_new_order_item, oper_record_log

            elif not buy_new_order and sell_new_order:
                new_order_item = sell_new_order[0]
                oper_record_log += "\n\nFilled-60、正在进行的卖出订单: %s 当前状态: %s" % (str(json.dumps(new_order_item)), str(new_order_item['side']))
                
                map_new_order_item, oper_record_log = get_map_buy_order_item(all_orders, new_order_item, oper_record_log)
                if map_new_order_item:
                    return True, new_order_item, map_new_order_item, oper_record_log
            
            return True, new_order_item, map_new_order_item, oper_record_log
    except Exception as e:
        send_exception(traceback.format_exc())

    oper_record_log += "\nFilled-90、订单详情都在进行中: 买入订单: %s 卖出订单: %s" % (str(json.dumps(buy_new_order)), str(json.dumps(sell_new_order)))
    oper_record_log += "\nFilled-99、最新的订单获取异常 账户: %s 币种: %s" % (str(account), str(symbol))
    return False, False, False, oper_record_log


def get_map_sell_order_item(all_orders, new_buy_order_item, oper_record_log):
    for key,item in enumerate(all_orders):
        if item['status'] == ORDER_STATUS_FILLED and item['type'] == 'LIMIT' and item['side'] == SIDE_SELL:
            buyClientOrderId = new_buy_order_item['clientOrderId'].split('666')[0]
            sellClientOrderId = item['clientOrderId'].split('777')[0]

            if sellClientOrderId == buyClientOrderId:
                map_sell_filled_order_item = item
                oper_record_log += "\nFilled-54、正在买入订单: %s 对应的卖出订单: %s " % (str(json.dumps(new_buy_order_item)), str(json.dumps(map_sell_filled_order_item)))
                return map_sell_filled_order_item, oper_record_log
    oper_record_log += "\nFilled-56、正在买入订单: %s 没有对应的卖出订单" % (str(json.dumps(new_buy_order_item)))
    return False, oper_record_log

def get_map_buy_order_item(all_orders, new_sell_order_item, oper_record_log):
    for key,item in enumerate(all_orders):
        if item['status'] == ORDER_STATUS_FILLED and item['type'] == 'LIMIT' and item['side'] == SIDE_BUY:
            buyClientOrderId = item['clientOrderId'].split('666')[0]
            sellClientOrderId = new_sell_order_item['clientOrderId'].split('777')[0]
            if buyClientOrderId == sellClientOrderId:
                map_buy_filled_order_item = item
                oper_record_log += "\nFilled-64、正在卖出订单: %s 对应的买入订单: %s " % (str(json.dumps(new_sell_order_item)), str(json.dumps(map_buy_filled_order_item)))
                return map_buy_filled_order_item, oper_record_log
    oper_record_log += "\nFilled-56、正在卖出订单: %s 没有对应的买入订单" % (str(json.dumps(new_sell_order_item)))
    return False, oper_record_log

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_same_auto_buy_sell()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

if __name__ == '__main__':
    main() 