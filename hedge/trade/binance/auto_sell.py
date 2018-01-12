# coding=utf-8
# 币安平台自动交易
# 卖出

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

from db_util import insert_binance_recent_trades_data, find_btc_binance_order_oper_buy, find_btc_binance_order_sell_record, find_btc_binance_order_sell_record_surplus, find_btc_binance_order_selling, find_btc_binance_order_buy_newest_one,find_btc_binance_order_buy_newest_one_not_all_sell, insert_btc_binance_order_stop_sell_record, find_btc_binance_order_stop_sell_record_newest_one
from binance_util import get_client, get_all_tickers, get_order_book, create_stop_sell_order, get_recent_trades, get_ticker, get_aggregate_trades, get_orderbook_tickers, get_open_orders, get_asset_balance, cancel_order, get_symbol_info, get_all_orders,get_klines
from account_util import get_account_list
from helper_util import id_generator
from common_util import common_sync_all_order, common_get_curr_max_price_recent

def start_sell():
        
    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])
        account = a_item['account']
        
        # 同步账户下的订单
        #common_sync_all_order(client, account)

        # 是否有卖出交易正在进行中
        is_selling = find_btc_binance_order_selling(account)
        if(is_selling):
            print "有卖出进行中"
            break

        # 获取上一次没有全部卖出的订单
        order_buy_newest_one_not_all_sell =  find_btc_binance_order_buy_newest_one_not_all_sell(account)

        if (order_buy_newest_one_not_all_sell):
            print "开始进行没有卖出的订单"
            origQty = order_buy_newest_one_not_all_sell['origQty'] 
            executedQty = order_buy_newest_one_not_all_sell['executedQty']
            sell_qty = origQty - executedQty
               
            sellClientOrderId = order_buy_newest_one_not_all_sell['sellClientOrderId']
            buy_price = order_buy_newest_one_not_all_sell['price']
            orderId = order_buy_newest_one_not_all_sell['orderId']

            time = int(order_buy_newest_one_not_all_sell['time'])

            # 获取当前最近的的交易中最高和最低价格
            min_price, max_price = get_recent_trade_max_min_price_by_trade_time(client, time)

            # 当最近交易价格中 最高价格 高于 买入价格,大于2.5% 才进入卖出逻辑
            is_sell = oper_is_sell(max_price, buy_price)

            if (is_sell):
                # 计算并获取 触发价格、止损价格 
                sell_price, stop_sell_price = get_stop_sell_price_order(max_price, buy_price)

                print "===================未卖出的开始卖出==================="
                print '最近交易最低价格: %s ; 最高价格: %s' % (min_price, max_price)
                print '触发价格: %s ; 止损价格: %s' % (sell_price, stop_sell_price)
                print '上一次买入价格: %s' % buy_price
                print '买入订单ID: %s' % orderId
                # 开始设置卖出止损
                set_stop_sell_price_order(client, sell_price, stop_sell_price, sell_qty, sellClientOrderId)
            else:
                print "===================未卖出的不可以==================="
                print '最近交易最低价格: %s ; 最高价格: %s' % (min_price, max_price)
                print '上一次买入价格: %s' % buy_price
                print '买入订单ID: %s' % orderId
        else:
            # 获取上一次买入的订单
            order_buy_newest_one = find_btc_binance_order_buy_newest_one(account)
            if(order_buy_newest_one):
                print "开始进行买入的订单"
                origQty = order_buy_newest_one['origQty'] 
                sellClientOrderId = order_buy_newest_one['sellClientOrderId']
                buy_price = order_buy_newest_one['price']
                orderId = order_buy_newest_one['orderId']
                time = int(order_buy_newest_one['time'])
                
                # 获取当前最近的的交易中最高和最低价格
                min_price, max_price = get_recent_trade_max_min_price_by_trade_time(client, time)

                # 当最近交易价格中 最高价格 高于 买入价格,大于2.5% 才进入卖出逻辑
                is_sell = oper_is_sell(max_price, buy_price)

                if (is_sell):
                    # 计算并获取 触发价格、止损价格 
                    sell_price, stop_sell_price = get_stop_sell_price_order(max_price, buy_price)

                    print "===================买入的开始卖出==================="
                    print '最近交易最低价格: %s ; 最高价格: %s' % (min_price, max_price)
                    print '触发价格: %s ; 止损价格: %s' % (sell_price, stop_sell_price)
                    print '上一次买入价格: %s' % buy_price
                    print '买入订单ID: %s' % orderId
                    # 开始设置卖出止损
                    set_stop_sell_price_order(client, sell_price, stop_sell_price, origQty, sellClientOrderId)
                else:
                    print "===================买入的不可以==================="
                    print '最近交易最低价格: %s ; 最高价格: %s' % (min_price, max_price)
                    print '上一次买入价格: %s' % buy_price
                    print '买入订单ID: %s' % orderId
            else:
                print "暂时没有订单要卖出"

        
# 最高价格是否大于买入价格的2.5%
def oper_is_sell(max_price, buy_price):
    sell_rate = (Decimal(max_price) - Decimal(buy_price))/Decimal(buy_price)
    sell_rate = round(sell_rate,8)
    if(sell_rate >= 0.025):
        return True
    return False

# 计算止损价格
def get_stop_sell_price_order(max_price, buy_price):
    stop_rate = float(Decimal(1) - (Decimal(max_price) - Decimal(buy_price))/Decimal(buy_price) * Decimal(0.05))
    stop_sell_price = round(float(max_price) * stop_rate,8)
    sell_price = round(float(Decimal(stop_sell_price) * Decimal(1.0005)),8)
    return sell_price, stop_sell_price


# 开始设置止损价格
def set_stop_sell_price_order(client, sell_price, stop_sell_price, sell_qty, sellClientOrderId):
    
    order_symbol = 'EOSBTC'
    order_side = SIDE_SELL
    order_type = ORDER_TYPE_TAKE_PROFIT_LIMIT
    order_timeInForce = TIME_IN_FORCE_GTC
    order_price = sell_price 
    order_stopPrice = stop_sell_price
    order_quantity = sell_qty
    
    # 对应买入的客户端ID
    parentClientOrderId = sellClientOrderId
    # 卖出的客户端ID
    newSellClientOrderId = '%s%s%s' % (sellClientOrderId,'66-66',str(int(time.time())))
    
    # 获取上一次设置的信息
    set_stop_sell_record_result = find_btc_binance_order_stop_sell_record_newest_one(parentClientOrderId)
    
    # 如果有设置,判断设置信息是否相同
    if(set_stop_sell_record_result):
        stopPrice = set_stop_sell_record_result['stopPrice'] # 上一次设置的止损价格
        price = set_stop_sell_record_result['price'] # 上一次设置的触发价格
        origQty = set_stop_sell_record_result['origQty'] # 上一次设置的数量
        orderId = set_stop_sell_record_result['orderId'] # 上一次设置的订单ID

        # 判断 触发价格、止损价格、购买数量是否相同; 如果相同,则不用设置;
        if( order_price == price and order_stopPrice == stopPrice and order_quantity == origQty):
            print "相同,不用设置"
        
        # 如果不相同,则取消订单 并重新设置
        else:
            print "重新设置止损"
            cancel_order(client, order_symbol, orderId)
            sell_order_result = create_stop_sell_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newSellClientOrderId)
            insert_btc_binance_order_stop_sell_record(sell_order_result, parentClientOrderId)
        
    # 第一次设置止损价格,触发价格、止损价格、数量
    else:
        print "第一次设置"
        sell_order_result = create_stop_sell_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newSellClientOrderId)
        insert_btc_binance_order_stop_sell_record(sell_order_result, parentClientOrderId)
       



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
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_sell()

if __name__ == '__main__':
    main() 