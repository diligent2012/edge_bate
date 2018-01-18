#!/usr/bin/python
#coding:utf-8
# 币安平台自动交易
# 买入

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

# 开始买入
def start_auto_buy():
    
    try:
        # is_allow = allow_send_time()
        # if not is_allow:
        #     return
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

                oper_record_log = "10、执行开始买入" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                oper_record_log += "\n20、账户: %s" % (account)
                oper_record_log += "\n30、币种: %s" % (symbol)

                # 同步账户下的订单
                oper_record_log = sync_all_order(client, account, symbol, start_auto_date, oper_record_log)

                # 查看是否有卖出单子在进行
                is_selling_rst, oper_record_log = is_selling(account, symbol, oper_record_log)

                # 查看当前是应该卖还是买
                is_start_buy_rst, oper_record_log = is_start_buy(account, symbol, oper_record_log)
                if(not is_selling_rst and is_start_buy_rst):

                    # 获取上一次卖出价格
                    prev_sell_price, order_time, oper_record_log = get_prev_sell_price(account, symbol, oper_record_log)

                    # 获取当前最近的的交易中最高和最低价格
                    min_price, max_price = get_recent_trade_max_min_price_by_trade_time(client, symbol, order_time)

                    oper_record_log += "\n70、当前交易中价格: 最高价: %s 最低价: %s " % (str(max_price), str(min_price))

                    if(prev_sell_price):

                        is_buy, oper_record_log = oper_is_buy(min_price, prev_sell_price, oper_record_log)
                        if (is_buy):

                            #计算触发、止盈价格
                            buy_price, stop_buy_price, oper_record_log = oper_stop_buy_price( min_price, prev_sell_price, oper_record_log)
                            
                            if (0.0 != buy_price and 0.0 != stop_buy_price):

                                # 止损价格必须高于买入价格。兜底做法
                                is_secure = secure_check(stop_buy_price, prev_sell_price)
                                if (is_secure):
                                    # 设置买入
                                    oper_record_log = set_stop_buy_price(client, stop_buy_price, buy_price, qty, symbol, oper_record_log)
                    else:
                        oper_record_log += "\n99、没有获取到上次卖出,请重视"
                       
                #记录所有日志
                insert_btc_binance_order_auto_log(account, 'BUY', symbol, oper_record_log)

    except Exception as e:
        send_exception(traceback.format_exc())

# 查看是否可以开始买入, 当没有卖出在进行的时候,可以买入
def is_start_buy(account, symbol, oper_record_log):
    try:
        buy_or_sell_rst = find_btc_binance_order_buy_or_sell(account, symbol) 
        if (SIDE_SELL == buy_or_sell_rst['side']):
            oper_record_log += "\n50-B、当前是要进行买入"
            return True, oper_record_log
        else:
            oper_record_log += "\n50-C、当前要进行卖出、当前不能买入"
    except Exception as e:
        send_exception(traceback.format_exc())

    return False, oper_record_log
# 是否有卖出在进行
def is_selling(account, symbol, oper_record_log):
    try:
        is_selling_result = find_btc_binance_order_selling(account, symbol)
        if(is_selling_result):
            for key,sell_item in enumerate(is_selling_result): 
                orderId = sell_item['orderId']
                symbol = sell_item['symbol']
                price = sell_item['price']
                stopPrice = sell_item['stopPrice']
                origQty = sell_item['origQty']
                executedQty = sell_item['executedQty']
                oper_record_log += "\n50、有卖出订单进行中: 订单ID: %s 币种: %s  触发价格: %s 止损价格: %s 需要卖出数量: %s 实际卖出数量: %s" % (str(orderId), str(symbol), str(price), str(stopPrice), str(origQty), str(executedQty))
            return True, oper_record_log
        else:
            oper_record_log += "\n50-D、没有卖出订单进行中"
    except Exception as e:
        send_exception(traceback.format_exc())
    return False, oper_record_log

# 最低价格是否小于上次卖出价格的2.5%
def oper_is_buy(min_price, sell_price, oper_record_log):
    try:
        buy_rate = (Decimal(sell_price) - Decimal(min_price))/Decimal(min_price)
        buy_rate = round(buy_rate,8)
        if(buy_rate >= 0.025):
            oper_record_log += "\n80-A、跌幅大于0.025: 最低价格: %s 卖出价格: %s 跌幅率: %s" % (str(min_price), str(sell_price), str(buy_rate))
            return True, oper_record_log
        oper_record_log += "\n80-B、跌幅小于0.025: 最低价格: %s 卖出价格: %s 跌幅率: %s" % (str(min_price), str(sell_price),  str(buy_rate))
    except Exception as e:
        send_exception(traceback.format_exc())
    return False, oper_record_log

# 计算止损价格
def oper_stop_buy_price(min_price, sell_price, oper_record_log):
    try:
        stop_rate = float(Decimal(1) + (Decimal(sell_price) - Decimal(min_price))/Decimal(min_price) * Decimal(0.2))
        stop_buy_price = round(float(min_price) * stop_rate,6)
        buy_price = round(float(Decimal(stop_buy_price) * Decimal(1.0005)),6)
        oper_record_log += "\n80-C、得出的设置价格: 触发价格: %s 止盈价格: %s " % (str(buy_price), str(stop_buy_price))
        return buy_price, stop_buy_price, oper_record_log
    except Exception as e:
        send_exception(traceback.format_exc())
    oper_record_log += "\n80-D、无法得出设置价格: 最低价格: %s 卖出价格: %s " % (str(min_price), str(sell_price))
    return 0.0, 0.0, oper_record_log


# 获取上一次卖出的价格
def get_prev_sell_price(account, symbol, oper_record_log):
    try:
        order_sell_newest_one = find_btc_binance_order_sell_newest_one(account, symbol)
        if(order_sell_newest_one):
            order_time = int(order_sell_newest_one['time']) #上一次卖出的时间
            orderId = order_sell_newest_one['orderId'] #上一次卖出的订单ID
            symbol = order_sell_newest_one['symbol'] #上一次卖出的币种
            price = order_sell_newest_one['price'] #上一次卖出的触发价格
            stopPrice = order_sell_newest_one['stopPrice'] #上一次卖出的止损价格
            origQty = order_sell_newest_one['origQty'] #上一次卖出的数量
            executedQty = order_sell_newest_one['executedQty'] #上一次卖出的实际数量
            oper_record_log += "\n60、上一次卖出数据: 订单ID: %s 币种: %s  触发价格: %s 止损价格: %s 需要卖出数量: %s 实际卖出数量: %s 卖出时间: %s" % (str(orderId), str(symbol), str(price), str(stopPrice), str(origQty), str(executedQty), format_time(order_time))
            
            return price, order_time, oper_record_log
    except Exception as e:
        send_exception(traceback.format_exc())
    return False, False, oper_record_log

# 开始设置止盈价格
def set_stop_buy_price(client, buy_price, stop_buy_price, buy_qty, symbol, oper_record_log):
    try:
        order_symbol = symbol
        order_side = SIDE_BUY
        order_type = ORDER_TYPE_TAKE_PROFIT_LIMIT
        order_timeInForce = TIME_IN_FORCE_GTC
        order_price = buy_price 
        order_stopPrice = stop_buy_price
        order_quantity = buy_qty

        # 获取上一次设置的信息
        set_stop_buy_record_result = find_btc_binance_order_stop_buy_record_newest_one(symbol)

        # 如果有设置,判断设置信息是否相同
        if(set_stop_buy_record_result):

            stopPrice = set_stop_buy_record_result['stopPrice'] # 上一次设置的止盈价格
            price = set_stop_buy_record_result['price'] # 上一次设置的触发价格
            origQty = set_stop_buy_record_result['origQty'] # 上一次设置的数量
            orderId = set_stop_buy_record_result['orderId'] # 上一次设置的订单ID

            if(order_stopPrice > stopPrice):
                oper_record_log += "\n90-D、大于上一次设置价格,不设置 设置价格: %s 上一次设置价格: %s " % (order_stopPrice, stopPrice)
            else:
                # 判断 触发价格、止盈价格、购买数量是否相同; 如果相同,则不用设置;
                if( order_price == price and order_stopPrice == stopPrice and order_quantity == origQty):
                    oper_record_log += "\n90-C、和上次设置止损相同 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_price, order_stopPrice, order_side, order_type, order_timeInForce)

                # 如果不相同,则取消订单 并重新设置
                else:
                    oper_record_log += "\n90-B、重新设置止损 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_price, order_stopPrice, order_side, order_type, order_timeInForce)
                    cancel_order(client, order_symbol, orderId)
                    buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
                    insert_btc_binance_order_stop_buy_record(buy_order_result)
        
        # 第一次设置止盈价格,触发价格、止盈价格、数量
        else:
            oper_record_log += "\n90-A、第一次设置止损 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_price, order_stopPrice, order_side, order_type, order_timeInForce)
            buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
            insert_btc_binance_order_stop_buy_record(buy_order_result)
    except Exception as e:
        send_exception(traceback.format_exc())
    finally:
        return oper_record_log
    return oper_record_log

def secure_check(stop_buy_price, prev_sell_price):
    if(stop_buy_price < prev_sell_price):
        return True
    return False

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_auto_buy()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

if __name__ == '__main__':
    main() 