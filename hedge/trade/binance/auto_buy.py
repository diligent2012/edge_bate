#!/usr/bin/python
#coding:utf-8
# 币安平台自动交易
# 买入

import sys,os
sys.path.append("../../platform/")
sys.path.append("../../util/")
reload(sys)
sys.setdefaultencoding('utf-8')
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *
from decimal import *

from db_util import insert_binance_recent_trades_data, find_btc_binance_order_sell_newest_one, find_btc_binance_order_record, insert_btc_binance_order_stop_buy_record, find_btc_binance_order_stop_buy_record_newest_one, find_btc_binance_order_buying
from binance_util import get_client, get_all_tickers, get_order_book, get_recent_trades, get_ticker, get_aggregate_trades, get_orderbook_tickers, get_open_orders,  get_asset_balance, cancel_order, get_symbol_info, get_all_orders, get_klines, create_stop_buy_order
from account_util import get_account_list
from helper_util import id_generator
from common_util import common_sync_all_order, common_get_curr_min_price_recent


# 开始买入
def start_buy():
    
    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])
        account = a_item['account']
        
        # 同步账户下的订单
        common_sync_all_order(client, account)

        # 是否有买入交易正在进行中
        is_buying = find_btc_binance_order_buying(account)
        if(is_buying):
            break

        # 获取上一次卖出的价格
        order_sell_newest_one = find_btc_binance_order_sell_newest_one(account)

        newest_one_sell_time = int(order_sell_newest_one['time']) #上一次卖出的时间
        newest_one_sell_origQty = order_sell_newest_one['origQty'] #上一次卖出的数量
        newest_one_sell_orderId = order_sell_newest_one['orderId'] #上一次卖出的订单ID
        newest_one_sell_price = order_sell_newest_one['price'] #上一次卖出的价格
        

        # 获取当前最近的的交易中最高和最低价格
        min_price, max_price = get_recent_trade_max_min_price_by_trade_time(client, newest_one_sell_time)
        # 当最近交易价格中 最低价格 低于 卖出价格,才进入买入逻辑
        if (min_price < newest_one_sell_price):

            # 计算并获取 触发价格、止盈价格 
            buy_price, stop_buy_price = get_stop_buy_price(min_price, newest_one_sell_price)

            # 开始设置买入止盈
            print "===================开始买入==================="
            print '最近交易最低价格: %s ; 最高价格: %s' % (min_price, max_price)
            print '触发价格: %s ; 止盈价格: %s' % (buy_price, stop_buy_price)
            print '上一次卖出价格: %s' % newest_one_sell_price
            print '卖出订单ID: %s' % newest_one_sell_orderId
            
            set_stop_buy_price_order(client, buy_price, stop_buy_price, newest_one_sell_origQty)
        else:
            print "===================不可以==================="
            print '最近交易最低价格: %s ; 最高价格: %s' % (min_price, max_price)
            print '上一次卖出价格: %s' % newest_one_sell_price
            print '卖出订单ID: %s' % newest_one_sell_orderId     
    
    
# 开始设置止盈价格
def set_stop_buy_price_order(client, buy_price, stop_buy_price, buy_qty):

    order_symbol = 'EOSBTC'
    order_side = SIDE_BUY
    order_type = ORDER_TYPE_TAKE_PROFIT_LIMIT
    order_timeInForce = TIME_IN_FORCE_GTC
    order_price = buy_price 
    order_stopPrice = stop_buy_price
    order_quantity = buy_qty

    # 获取上一次设置的信息
    set_stop_buy_record_result = find_btc_binance_order_stop_buy_record_newest_one()
    # 如果有设置,判断设置信息是否相同
    if(set_stop_buy_record_result):

        stopPrice = set_stop_buy_record_result['stopPrice'] # 上一次设置的止盈价格
        price = set_stop_buy_record_result['price'] # 上一次设置的触发价格
        origQty = set_stop_buy_record_result['origQty'] # 上一次设置的数量
        orderId = set_stop_buy_record_result['orderId'] # 上一次设置的订单ID

        # 判断 触发价格、止盈价格、购买数量是否相同; 如果相同,则不用设置;
        if( order_price == price and order_stopPrice == stopPrice and order_quantity == origQty):
            print "相同,不用设置"

        # 如果不相同,则取消订单 并重新设置
        else:
            print "重新设置止损"
            cancel_order(client, order_symbol, orderId)
            buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
            insert_btc_binance_order_stop_buy_record(buy_order_result)
    
    # 第一次设置止盈价格,触发价格、止盈价格、数量
    else:
        print "第一次设置"
        buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
        insert_btc_binance_order_stop_buy_record(buy_order_result)

# 计算买入触发价格和止盈价格              
def get_stop_buy_price(min_price, sell_price):
    stop_rate = float(Decimal(1) - (Decimal(sell_price) - Decimal(min_price))/Decimal(min_price) * Decimal(0.05))
    stop_buy_price = round(float(sell_price) * stop_rate,8)
    buy_price = round(float(Decimal(stop_buy_price) * Decimal(1 - 0.0005)),8)
    return buy_price, stop_buy_price

# 根据上一次交易时间,获取之后的最近交易记录中最高和最低价格
def get_recent_trade_max_min_price_by_trade_time(client, trade_time = 0):

    recent_trades = get_recent_trades(client)
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


# 入口方法
def main():
    #执行时间
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_buy()

if __name__ == '__main__':
    main() 