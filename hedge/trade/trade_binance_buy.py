# coding=utf-8
# 币安平台自动交易
# 买入

import sys,os
sys.path.append("../platform/")
sys.path.append("../util/")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *
from decimal import *

from db_util import insert_binance_recent_trades_data, find_btc_binance_order_oper_sell, find_btc_binance_order_record, insert_btc_binance_order_stop_buy_record, find_btc_binance_order_stop_buy_record, find_btc_binance_order_buying
from binance_util import get_client, get_all_tickers, get_order_book, get_recent_trades, get_ticker, get_aggregate_trades, get_orderbook_tickers, get_open_orders,  get_asset_balance, cancel_order, get_symbol_info, get_all_orders, get_klines, create_stop_buy_order
from account_util import get_account_list
from helper_util import id_generator

from common_util import common_sync_all_order, common_get_curr_min_price_recent


# 代码执行针对订单有效时间
#LIMIT_DATE = '2018-01-07 00:00:00'

def start_trade_buy():

    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])
        account = a_item['account']

        # 同步已经成交的订单
        common_sync_all_order()
        
        is_buying = find_btc_binance_order_buying(account)
        if(is_buying):
            break

        btc_binance_trade = find_btc_binance_order_oper_sell(account)
        if(btc_binance_trade):
            for key,item in enumerate(btc_binance_trade):
                if 0 == key:
                    status = item['status']
                    side = item['side']
                    origQty = item['origQty']
                    #executedQty = item['executedQty']
                    orderId = item['orderId']
                    sell_price = item['price']

                    curr_min_price = common_get_curr_min_price_recent(client)

                    # 当前价格 大于 最近卖出价格,不买入
                    if(curr_min_price > sell_price):
                        print "不买入", curr_min_price, sell_price
                        print '当前最低价格: %s' % curr_min_price
                        print '最近卖出价格: %s ; 卖出数量: %s' % (sell_price, origQty)
                        break
                    
                    buy_price, stop_buy_price = oper_buy_price(curr_min_price, sell_price)
                    print buy_price, stop_buy_price

                    if ('FILLED' == status):
                        print "===================第一档==================="
                        print '当前最低价格: %s' % curr_min_price
                        print '卖出订单ID: %s' % orderId
                        print '最近卖出价格: %s ; 卖出数量: %s' % (sell_price, origQty)
                        print '触发价格: %s ; 止损价格: %s' % (buy_price, stop_buy_price)
                        set_stop_price_order(client, buy_price, stop_buy_price, origQty)
      
# 计算买入触发价格和止损价格              
def oper_buy_price(curr_min_price, sell_price):
    stop_rate = float(Decimal(1) - (Decimal(sell_price) - Decimal(curr_min_price))/Decimal(curr_min_price) * Decimal(0.05))
    stop_buy_price = round(float(sell_price) * stop_rate,8)
    buy_price = round(float(Decimal(stop_buy_price) * Decimal(1 - 0.0005)),8)
    return buy_price, stop_buy_price
   


# 开始设置止盈价格
def set_stop_price_order(client, buy_price, stop_buy_price, buy_qty):
    order_symbol = 'EOSBTC'
    order_side = SIDE_BUY
    order_type = ORDER_TYPE_TAKE_PROFIT_LIMIT
    order_timeInForce = TIME_IN_FORCE_GTC
    order_price = buy_price 
    order_stopPrice = stop_buy_price
    order_quantity = buy_qty
    print order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice
    #检查是否和上一次设置的止盈价格相同,如果相同,则不用取消重新设置; 如果不相同,则取消重新设置
    set_stop_record_buy_result = find_btc_binance_order_stop_buy_record()
    if(set_stop_record_buy_result):

        stopPrice = set_stop_record_buy_result['stopPrice']
        price = set_stop_record_buy_result['price']
        origQty = set_stop_record_buy_result['origQty']
        orderId = set_stop_record_buy_result['orderId']

        # 判断 触发价格、止盈价格、购买数量是否相同; 如果相同,则不用取消重新设置; 如果不相同,则取消重新设置
        if( order_price == price and order_stopPrice == stopPrice and order_quantity == origQty):
            print "相同,不用设置"
        else:
            print "重新设置止损"
            cancel_order(client, order_symbol, orderId)
            buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
            insert_btc_binance_order_stop_buy_record(buy_order_result)
    else:
        print "第一次设置"
        buy_order_result = create_stop_buy_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
        insert_btc_binance_order_stop_buy_record(buy_order_result)

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_trade_buy()

if __name__ == '__main__':
    main() 