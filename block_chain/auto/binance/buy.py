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

from setting import *
from db import *
from util import *
from helper import *


# 开始买入
def start_buy():
    account_list = get_account_list()
    #binance_symbols = get_binance_symbols()
    # 循环不同的账户
    for key,a_item in enumerate(account_list):

        client = Client(a_item['api_key'], a_item['api_secret'])
        account = a_item['account']
        #symbol = 'EOSBTC'
        binance_symbols = a_item['allow_symbol']
        
        # 循环不同的币种
        for key,s_item in enumerate(binance_symbols): 
            symbol = s_item['symbol']

            oper_record_log = "执行开始买入" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

            oper_record_log += "\n账户: %s" % (account)

            oper_record_log += "\n币种: %s" % (symbol)

            # 同步账户下的订单
            oper_record_log = sync_all_order(client, account, symbol, oper_record_log)

            #当没有卖出的时候,开始买入
            is_selling_result = find_btc_binance_order_selling(account, symbol)
            if(is_selling_result):
                for key,sell_item in enumerate(is_selling_result): 
                    orderId = sell_item['orderId']
                    symbol = sell_item['symbol']
                    price = sell_item['price']
                    stopPrice = sell_item['stopPrice']
                    origQty = sell_item['origQty']
                    executedQty = sell_item['executedQty']
                    oper_record_log += "\n有卖出订单进行中: 订单ID: %s 币种: %s  触发价格: %s 止损价格: %s 需要卖出数量: %s 实际卖出数量: %s" % (str(orderId), str(symbol), str(price), str(stopPrice), str(origQty), str(executedQty))
            else:

                # 获取最近一次卖出的交易数据
                order_sell_newest_one = find_btc_binance_order_sell_newest_one(account, symbol)

                if(order_sell_newest_one):

                    order_time = int(order_sell_newest_one['time']) #上一次卖出的时间
                    orderId = order_sell_newest_one['orderId'] #上一次卖出的订单ID
                    symbol = order_sell_newest_one['symbol'] #上一次卖出的币种
                    price = order_sell_newest_one['price'] #上一次卖出的触发价格
                    stopPrice = order_sell_newest_one['stopPrice'] #上一次卖出的止损价格
                    origQty = order_sell_newest_one['origQty'] #上一次卖出的数量
                    executedQty = order_sell_newest_one['executedQty'] #上一次卖出的实际数量
                                        
                    oper_record_log += "\n上一次卖出数据: 订单ID: %s 币种: %s  触发价格: %s 止损价格: %s 需要卖出数量: %s 实际卖出数量: %s 卖出时间: %s" % (str(orderId), str(symbol), str(price), str(stopPrice), str(origQty), str(executedQty), format_time(order_time))
                    
                    # 获取当前最近的的交易中最高和最低价格
                    min_price, max_price = get_recent_trade_max_min_price_by_trade_time(client, symbol, order_time)

                    oper_record_log += "\n当前交易中价格: 最高价: %s 最低价: %s " % (str(max_price), str(min_price))

                    # 当最近交易价格中 最低价格 低于 卖出价格,才进入买入逻辑
                    if (min_price < stopPrice):

                        oper_record_log += "\n价格比较可以买入: 上次卖出价格: %s 最低价: %s " % (str(stopPrice), str(min_price))

                        # 计算并获取 触发价格、止盈价格 
                        buy_price, stop_buy_price = get_stop_buy_price(min_price, stopPrice)

                        oper_record_log += "\n得出的设置价格: 触发价格: %s 止盈价格: %s " % (str(buy_price), str(stop_buy_price))

                        oper_record_log = set_stop_buy_price_order(client, buy_price, stop_buy_price, executedQty, symbol, oper_record_log)

                    else:
                        oper_record_log += "\n最低价格高于卖出价格: 最低价: %s 上次卖出价格: %s " % (str(min_price), str(stopPrice))

                else:
                    #如果没有,提醒手动买入
                    oper_record_log += "\n获取不到上次卖出数据,请手动买入: 账户: %s 币种: %s " % (str(account), str(symbol))
                    
            insert_btc_binance_order_auto_log(account, 'BUY', symbol, oper_record_log)

            
# 开始设置止盈价格
def set_stop_buy_price_order(client, buy_price, stop_buy_price, buy_qty, symbol, oper_record_log):

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

        # 判断 触发价格、止盈价格、购买数量是否相同; 如果相同,则不用设置;
        if( order_price == price and order_stopPrice == stopPrice and order_quantity == origQty):
            oper_record_log += "\和上次设置止损相同 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_price, order_stopPrice, order_side, order_type, order_timeInForce)

        # 如果不相同,则取消订单 并重新设置
        else:
            oper_record_log += "\重新设置止损 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_price, order_stopPrice, order_side, order_type, order_timeInForce)
            cancel_order(client, order_symbol, orderId)
            buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
            insert_btc_binance_order_stop_buy_record(buy_order_result)
    
    # 第一次设置止盈价格,触发价格、止盈价格、数量
    else:
        oper_record_log += "\第一次设置止损 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_price, order_stopPrice, order_side, order_type, order_timeInForce)
        buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
        insert_btc_binance_order_stop_buy_record(buy_order_result)

    return oper_record_log

# 计算买入触发价格和止盈价格              
def get_stop_buy_price(min_price, sell_price):
    stop_rate = float(Decimal(1) - (Decimal(sell_price) - Decimal(min_price))/Decimal(min_price) * Decimal(0.05))
    stop_buy_price = round(float(sell_price) * stop_rate,8)
    buy_price = round(float(Decimal(stop_buy_price) * Decimal(1 - 0.0005)),8)
    return buy_price, stop_buy_price

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_buy()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

if __name__ == '__main__':
    main() 