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

# 开始同时买入和卖出
def start_same_auto_buy_sell():
    
    try:
        account_list = get_same_account_list()
        # 循环不同的账户
        for key,a_item in enumerate(account_list):
            client = Client(a_item['api_key'], a_item['api_secret'])
            account = a_item['account']
            qty = a_item['qty']
            start_auto_date = format_time_for_date(a_item['start_auto_date'])
            binance_symbols = a_item['allow_symbol']
            
            # 循环不同的币种
            for key,s_item in enumerate(binance_symbols): 
                symbol = s_item['symbol']

                oper_record_log = "Common-10、执行同时买卖开始" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                oper_record_log += "\nCommon-20、账户: %s" % (account)
                oper_record_log += "\nCommon-30、币种: %s" % (symbol)
                                
                # 获取最新的订单
                oper_record_log += "\nCommon-40、获取最新的订单 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                new_order, oper_record_log = get_newest_valid_order(client, account, symbol, oper_record_log)
                oper_record_log += "\nCommon-40、获取最新的订单 结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )

                side = 'same'

                # 如果正在进行订单,则继续进行
                if new_order:
                    oper_record_log += "\nCommon-45、有订单在买入或者卖出, 这时候就要注意了%s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                    
                # elif filled_order:
                    
                #     # 判断当前是应该买入还是卖出
                #     if(SIDE_SELL == filled_order['side']): # 如果当前获取到的是卖出,那么现在就要买入
                #         side = SIDE_BUY
                #         oper_record_log += "\nCommon-50、自动买入 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                #         oper_record_log = same_auto_buy(client, account, symbol, qty, filled_order, oper_record_log)
                #         oper_record_log += "\nCommon-50、自动买入 结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                        
                #     if(SIDE_BUY == filled_order['side']): # 如果当前获取到的是买入,那么现在就要卖出
                #         side = SIDE_SELL
                #         oper_record_log += "\nCommon-60、自动卖出 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                #         oper_record_log = same_auto_sell(client, account, symbol, qty, filled_order, oper_record_log)
                #         oper_record_log += "\nCommon-60、自动卖出 结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                else:
                    # 同时设定买入和卖出
                    oper_record_log += "\nCommon-90 同时设定买入和卖出订单 开始: %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                    oper_record_log = same_auto_buy_sell(client, account, symbol, qty, oper_record_log)
                    oper_record_log += "\nCommon-90 同时设定买入和卖出订单 结束: %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )

                oper_record_log += "\nCommon-99、执行同时买卖结束 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                insert_btc_binance_order_auto_log(account, side, symbol, oper_record_log)
    except Exception as e:
        send_exception(traceback.format_exc())


#----------------------------------------------------下面是买入-------------------------------------------------------

def same_auto_buy_sell(client, account, symbol, qty, oper_record_log):
    # 获取当前最近的的交易中最高和最低价格
    oper_record_log += "\nBuy-10、获取最高最低价格 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
    min_price, max_price = get_recent_trade_max_min_price_by_trade_time_six(client, symbol, 0)
    oper_record_log += "\nBuy-10-1、当前最高价格: %s 当前最低价格: %s " % (str(max_price), str(min_price))
    oper_record_log += "\nBuy-20、获取最高最低价格  结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )

    # 判断是否有利润,并且获取买入价格、卖出价格
    is_allow_buy_sell, buy_price, sell_price, confirm_rate, rate = oper_same_buy_sell_price(min_price, max_price)
    oper_record_log += "\nBuy-30、是否有利润: %s 确认利润率: %s 最初利润率: %s 卖出价格: %s 买入价格: %s" % (str(is_allow_buy_sell), str(confirm_rate), str(rate), str(sell_price), str(buy_price))

    if is_allow_buy_sell:

        buy_price = round(buy_price, 8)
        sell_price = round(sell_price, 8)

        # 卖出价格 必须 大于 买入价格。兜底做法(以防意外)
        is_secure = same_buy_sell_secure_check(buy_price, sell_price)
        oper_record_log += "\nBuy-50、是否安全: %s 止盈价格: %s 卖出价格: %s" % (str(is_secure), str(buy_price), str(sell_price))
        if is_secure:
            pass
            # 设置买入
            #oper_record_log = set_same_limit_buy_sell_price(client, account, buy_price, sell_price, qty, symbol, oper_record_log)

    return oper_record_log

# 卖出价格 必须 大于 买入价格。兜底做法(以防意外)
def same_buy_sell_secure_check(buy_price, sell_price):
    if(buy_price < sell_price):
        return True
    return False

# 判断是否有利润,并且获取买入价格、卖出价格
def oper_same_buy_sell_price(min_price, max_price):
        
    # 买入价格偏移幅度(上调)
    buy_price_offset = 0.6
    # 卖出价格偏移幅度(下调)
    sell_price_offset = 0.4

    # 固定利润比
    profit_rate = 0.002

    # 最高价格 和 最低价格的偏差幅度
    rate = 0.0
    try:

        rate = round((max_price - min_price)/min_price,4)

        if(rate >= 0.003):
            free_rate = rate - profit_rate

            buy_price = free_rate * buy_price_offset * min_price + min_price

            sell_price = max_price / ((free_rate * sell_price_offset) + 1 ) 
            
            confirm_rate = round( (sell_price - buy_price) / buy_price, 4)
            if(confirm_rate >= profit_rate):
                return True, buy_price, sell_price, confirm_rate, rate
    except Exception as e:
        send_exception(traceback.format_exc())
    return False, 0.0, 0.0, 0.0, rate

# 开始设置买入和卖出限价单
def set_same_limit_buy_sell_price(client, account, buy_price,  sell_price, qty, symbol, oper_record_log):
    try:
        order_symbol = symbol
        order_type = ORDER_TYPE_LIMIT
        order_price = buy_price  # 买入价格
        order_quantity = qty
        buyClientOrderId = id_generator()
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
            sellClientOrderId = '%s%s%s' % (buyClientOrderId,'666',str(int(time.time())))
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
                oper_record_log += "\nSell-Set-90、买入成功,但是卖出失败: %s " % (str(json.dumps(buy_order_result)), str(sell_order_result))
        else:
            oper_record_log += "\nSell-Set-91、买入失败,也就没有进行卖出: %s " % (str(buy_order_result))
    except Exception as e:
        send_exception(traceback.format_exc())
    finally:
        return oper_record_log
    return oper_record_log

#----------------------------------------------------下面是公共部分-------------------------------------------------------

# 获取最新订单 code: Filled-*
def get_newest_valid_order(client, account, symbol,oper_record_log):
    try:
        all_orders = client.get_all_orders(symbol = symbol);

        #filled_order = []
        new_order = []

        #filled_order_item = {}
        new_order_item = {}
        for key,item in enumerate(all_orders):
            # if item['status'] == ORDER_STATUS_FILLED and item['type'] == 'LIMIT':
            #     filled_order.append(item)

            if item['status'] == ORDER_STATUS_NEW and item['type'] == 'LIMIT' and item['side'] in [SIDE_BUY,SIDE_SELL]:
                new_order.append(item)

        # if filled_order:
        #     for key,item in enumerate(filled_order):
        #         if(len(filled_order) - 1 == key):
        #             filled_order_item = item
        #             oper_record_log += "\nFilled-10、最新的订单: %s 当前买卖状态: %s" % (str(json.dumps(filled_order_item)), str(filled_order_item['side']))

        if new_order:
            for key,item in enumerate(new_order):
                if(len(new_order) - 1 == key):
                    new_order_item = item
                    oper_record_log += "\nFilled-20、正在进行的订单: %s 当前买卖状态: %s" % (str(json.dumps(new_order_item)), str(new_order_item['side']))
        return  new_order_item, oper_record_log
        #return filled_order_item, new_order_item, oper_record_log
    except Exception as e:
        send_exception(traceback.format_exc())

    oper_record_log += "\nFilled-90、最新的订单获取异常 账户: %s 币种: %s" % (str(account), str(symbol))
    return False, oper_record_log
    #return False, False, oper_record_log

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_same_auto_buy_sell()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

if __name__ == '__main__':
    main() 