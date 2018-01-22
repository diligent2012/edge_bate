#!/usr/bin/python
#coding:utf-8
# 币安平台自动交易
# 买入、卖出集合在一起

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

# 开始买入和卖出
def start_single_auto_buy():
    
    try:
        account_list = get_account_list()
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

                oper_record_log = "Common-10、执行开始" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                oper_record_log += "\nCommon-20、账户: %s" % (account)
                oper_record_log += "\nCommon-30、币种: %s" % (symbol)
                                
                oper_record_log += "\nCommon-50、自动买入 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )

                sell_price = 0.00119515
                sell_order_time = 0

                oper_record_log = auto_buy(client, account, symbol, qty, sell_price, sell_order_time, oper_record_log)
                oper_record_log += "\nCommon-50、自动买入 结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )

                oper_record_log += "\nnCommon-99、执行结束 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
                insert_btc_binance_order_auto_log(account, SIDE_BUY, symbol, oper_record_log)
    except Exception as e:
        send_exception(traceback.format_exc())

#----------------------------------------------------下面是买入-------------------------------------------------------

# 自动买入程序 code: Buy-*
def auto_buy(client, account, symbol, qty, sell_price, sell_order_time, oper_record_log):

    # 获取当前最近的的交易中最高和最低价格
    oper_record_log += "\nBuy-10、获取最高最低价格 开始时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
    min_price, max_price = get_recent_trade_max_min_price_by_trade_time(client, symbol, sell_order_time)
    oper_record_log += "\nBuy-10-1、当前最高价格: %s 当前最低价格: %s " % (str(max_price), str(min_price))
    oper_record_log += "\nBuy-20、获取最高最低价格  结束时间 %s " % ( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) )
    
    # 判断是否有利润存在 
    is_allow_buy, buy_rate = oper_buy_profit(min_price, sell_price)
    oper_record_log += "\nBuy-30、是否有利润: %s 利润率: %s 卖出价格: %s 当前最低价格: %s" % (str(is_allow_buy), str(buy_rate), str(sell_price), str(min_price))

    if is_allow_buy:
        # 计算并获取 触发、止盈价格
        stop_buy_price, buy_price = oper_stop_buy_price( min_price, sell_price )
        oper_record_log += "\nBuy-40、计算止盈价格: 触发价格: %s 止盈价格: %s 当前最低价格: %s 卖出价格: %s" % (str(stop_buy_price), str(buy_price), str(min_price), str(sell_price))

        # 止盈价格 必须 低于 卖出价格。兜底做法(以防意外)
        is_secure = buy_secure_check(buy_price, sell_price)
        oper_record_log += "\nBuy-50、是否安全: %s 止盈价格: %s 卖出价格: %s" % (str(is_secure), str(buy_price), str(sell_price))
        if is_secure:
            # 设置买入
            oper_record_log = set_stop_buy_price(client, account, buy_price, stop_buy_price, qty, symbol, oper_record_log)
    
    return oper_record_log

# 计算买入利润
def oper_buy_profit(min_price, sell_price):
    buy_rate = 0.0
    try:
        buy_rate = ( Decimal(sell_price) - Decimal(min_price) ) / Decimal(min_price)
        buy_rate = round(buy_rate,8)
        if(buy_rate >= 0.025):
            return True, buy_rate
    except Exception as e:
        send_exception(traceback.format_exc())
    return False, buy_rate

# 计算止盈价格
def oper_stop_buy_price(min_price, sell_price):
    try:
        stop_rate = float(Decimal(1) + ((( Decimal(sell_price) - Decimal(min_price) ) / Decimal(min_price)) * Decimal(0.2)))
        buy_price = round(float(min_price) * stop_rate,6) #止盈价格

        stop_buy_price = round(float(Decimal(buy_price) * Decimal(1 - 0.0005)),6) #触发价格
        return stop_buy_price, buy_price
    except Exception as e:
        send_exception(traceback.format_exc())
    return 0.0, 0.0

# 买入安全检查
def buy_secure_check(buy_price, sell_price):
    if(buy_price < sell_price):
        return True
    return False

# 开始设置止盈价格
def set_stop_buy_price(client, account, buy_price, stop_buy_price, buy_qty, symbol, oper_record_log):
    try:
        order_symbol = symbol
        order_side = SIDE_BUY
        order_type = ORDER_TYPE_STOP_LOSS_LIMIT
        order_timeInForce = TIME_IN_FORCE_GTC
        order_price = buy_price  # 止盈价格
        order_stopPrice = stop_buy_price  # 触发价格
        order_quantity = buy_qty
        clientOrderId = id_generator()

        # 获取上一次设置的信息
        set_stop_buy_record_result = find_btc_binance_order_stop_buy_record_newest_one(account, symbol)

        # 如果有设置,判断设置信息是否相同
        if(set_stop_buy_record_result):
            stopPrice = set_stop_buy_record_result['stopPrice'] # 上一次设置的触发价格
            price = set_stop_buy_record_result['price'] # 上一次设置的止盈价格
            origQty = set_stop_buy_record_result['origQty'] # 上一次设置的数量
            orderId = set_stop_buy_record_result['orderId'] # 上一次设置的订单ID
            if(order_price > price):
                oper_record_log += "\nBuy-Set-10、大于上一次设置价格,不设置 设置价格: %s 上一次设置价格: %s " % (order_price, price)
            else:
                # 判断 触发价格、止盈价格、购买数量是否相同; 如果相同,则不用设置;
                if( order_stopPrice == stopPrice and order_price == price and order_quantity == origQty):
                    oper_record_log += "\nBuy-Set-20、和上次设置止损相同 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_stopPrice, order_price, order_side, order_type, order_timeInForce)

                # 如果不相同,则取消订单 并重新设置
                else:
                    oper_record_log += "\nBuy-Set-30、重新设置止损 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_stopPrice, order_price, order_side, order_type, order_timeInForce)
                    # cancel_order(client, order_symbol, orderId)
                    # buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
                    # insert_btc_binance_order_stop_buy_record(buy_order_result)
        
        # 第一次设置止盈价格,触发价格、止盈价格、数量
        else:
            oper_record_log += "\nBuy-Set-40、第一次设置止损 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_stopPrice, order_price, order_side, order_type, order_timeInForce)
            # buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
            # insert_btc_binance_order_stop_buy_record(buy_order_result)
    except Exception as e:
        send_exception(traceback.format_exc())
    finally:
        return oper_record_log
    return oper_record_log


# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_single_auto_buy()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

if __name__ == '__main__':
    main() 