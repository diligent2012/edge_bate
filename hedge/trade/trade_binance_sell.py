# coding=utf-8
# 币安平台自动交易
# 
# 什么时候买呢 
# 比较当前买的价格,精确到5位数
# 然后降低1个百分点买,如果
# 
# 什么时候卖
# 获取当前订单卖出的前3个的价格和数量

import sys,os
sys.path.append("../platform/")
sys.path.append("../util/")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *
from decimal import *

from db_util import insert_binance_recent_trades_data, find_btc_binance_order_oper, find_btc_binance_order_sell_record, find_btc_binance_order_sell_record_surplus, insert_btc_binance_order_stop_record, find_btc_binance_order_stop_record
from binance_util import get_client, get_all_tickers, get_order_book, create_stop_order, get_recent_trades, get_ticker, get_aggregate_trades, get_orderbook_tickers, get_open_orders, get_asset_balance, cancel_order, get_symbol_info, get_all_orders,get_klines
from account_util import get_account_list
from helper_util import id_generator


def start_trade_sell():

    # 获取当前买入(还没有卖出的)的订单,准备卖出
    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])
        account = a_item['account']
        # 同步已经成交的卖出订单
        #sync_sell_filled_trade(client)
        
        btc_binance_trade = find_btc_binance_order_oper(account)
        if(btc_binance_trade):
            for key,item in enumerate(btc_binance_trade):
                #print item
                origQty = item[5]
                executedQty = item[7]
                status = item[11]
                side = item[9]
                sellClientOrderId = item[2]
                buy_price = item[16]

                curr_max_price =get_curr_max_price_klines(client)

                is_sell_record = False # 是否存在对应的卖出纪录, 没有则进入,有的话就跳过
                
                is_find_btc_binance_order_sell_record = find_btc_binance_order_sell_record(account, sellClientOrderId)
                if is_find_btc_binance_order_sell_record:
                    is_sell_record = True

                is_sell_surplus = False # 是否对应的卖出还有剩余, 有剩余则进入,没有的就跳过
                surplus_qty = 0.0 # 剩余数量

                is_sell_surplus, surplus_qty = get_sell_surplus(account, sellClientOrderId, executedQty)



                # 买入的要卖出 (条件为: 状态为完成的、买卖类型为买、对应的卖出纪录不存在)
                if(status == 'FILLED' and 'BUY' == side):
                    if(not is_sell_record):
                        print item, "01"
                        print curr_max_price
                        sell_price, stop_sell_price = oper_stop_price(curr_max_price, buy_price)
                        set_stop_price_order(client, sell_price, stop_sell_price, executedQty, sellClientOrderId)

                # 买入的要卖出 (条件为: 状态为完成的、买卖类型为买、对应的卖出纪录存在, 但是数量不相等的)
                # if (status == 'FILLED' and 'BUY' == side):
                #     if(is_sell_surplus):
                #         print item, "02"


                # # 买入的部分要卖出 (条件为: 状态为完成的、买卖类型为买、对应的卖出纪录不存在)
                # if(status == 'CANCELED' and 'BUY' == side and origQty > executedQty and 0.0 != executedQty):
                #     if(not is_sell_record):
                #         print item, "03"

                # # 买入的部分要卖出 (条件为: 状态为完成的、买卖类型为买、对应的卖出纪录存在, 但是数量不相等的)
                # if (status == 'CANCELED' and 'BUY' == side and origQty > executedQty and 0.0 != executedQty):
                #     if(is_sell_surplus):
                #         print item , "04"
                
                
                # newClientOrderId =  item[-1]
                # buy_price = item[3]
                # buy_qty = item[4]
                # #sug_sell_price = round(buy_price * 1.06,8)
                # curr_max_price =get_curr_max_price(client)

                # stop_rate = float(Decimal(1.01) - (Decimal(curr_max_price) - Decimal(buy_price))/Decimal(buy_price) * Decimal(0.2))
                
                # stop_sell_price = round(float(curr_max_price) * stop_rate,8)
               
                # print "止损价格: %s" % str(stop_sell_price)

               
                  #update_btc_binance_trade_sell_order_id(sell_order_id, newClientOrderId)


def oper_is_sell(stop_sell_price, buy_price):
    (stop_sell_price - buy_price)/buy_price

    sell_rate = (Decimal(stop_sell_price) - Decimal(buy_price))/Decimal(buy_price)
    sell_rate = round(sell_rate,8)
    if(sell_rate >= 2.5):
        print sell_rate


def set_stop_price_order(client, sell_price, stop_sell_price, buy_qty, newClientOrderId):
    order_symbol = 'EOSBTC'
    order_side = SIDE_SELL
    order_type = ORDER_TYPE_TAKE_PROFIT_LIMIT
    order_timeInForce = TIME_IN_FORCE_GTC
    order_price = sell_price 
    order_stopPrice = stop_sell_price
    order_quantity = buy_qty
    print order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newClientOrderId
    
    # parentClientOrderId = newClientOrderId
    # newClientOrderId = '%s%s%s' % (newClientOrderId,'66-66',str(int(time.time())))
    # #检查是否和上一次设置的止损价格相同,如果相同,则不用取消重新设置; 如果不相同,则取消重新设置
    # set_stop_record_result = find_btc_binance_order_stop_record(parentClientOrderId)
    # if(set_stop_record_result):
    #     stopPrice = set_stop_record_result[8]
    #     price = set_stop_record_result[11]
    #     origQty = set_stop_record_result[3]
    #     orderId = set_stop_record_result[1]

    #     # 判断 触发价格、止损价格、购买数量是否相同; 如果相同,则不用取消重新设置; 如果不相同,则取消重新设置
    #     if( order_price == price and order_stopPrice == stopPrice and order_quantity == origQty):
    #         print "相同"
    #     else:
    #         print "不相同"
    #         print orderId
    #         cancel_order(client, order_symbol, orderId)
    #         sell_order_result = create_stop_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newClientOrderId )
    #         print sell_order_result
    #         insert_btc_binance_order_stop_record(sell_order_result, parentClientOrderId)
    # else:
    #     print "无"
    #     sell_order_result = create_stop_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newClientOrderId )
    #     print sell_order_result
    #     insert_btc_binance_order_stop_record(sell_order_result, parentClientOrderId)


def oper_stop_price(curr_max_price, buy_price):
    stop_rate = float(Decimal(1) - (Decimal(curr_max_price) - Decimal(buy_price))/Decimal(buy_price) * Decimal(0.05))
    stop_sell_price = round(float(curr_max_price) * stop_rate,8)
    sell_price = round(float(Decimal(stop_sell_price) * Decimal(1.0005)),8)
    return sell_price, stop_sell_price


def get_sell_surplus(account, sellClientOrderId, buy_qty):
    btc_binance_order_sell_record_surplus = find_btc_binance_order_sell_record_surplus(account, sellClientOrderId)
    execute_sell_qty = 0.0
    if btc_binance_order_sell_record_surplus :
            for key,item in enumerate(btc_binance_order_sell_record_surplus):
                #origQty = item[5]
                executedQty = item[7]
                execute_sell_qty += executedQty
    else:
        return False, 0.0

    if buy_qty > execute_sell_qty:
        # 剩余数量
        surplus_qty = buy_qty - execute_sell_qty
        return True, surplus_qty

    return False, 0.0
    
# 获取当前交易的最高价格
def get_curr_max_price_recent(client):
    recent_trades = get_recent_trades(client)
    max_price = 0.0
    for key,item in enumerate(recent_trades):
        if(0 == key):
            max_price = item['price']
        else:
            if(item['price'] > max_price):
                max_price = item['price']
    
    # 将当前最高价格提高百分比
    max_price = float(max_price) * float(1.1)
    return round(max_price,8)



def get_curr_max_price_klines(client):
    klines = get_klines(client)
    max_price = 0.0
    ratio_num = 5
    for key,item in enumerate(klines):
        if(key > len(klines) - ratio_num):
            if(key == len(klines) - ratio_num):
                max_price = item[2]
            else:
                if(item[2] > max_price):
                    max_price = item[2]
    return max_price


# 同步已经成交的卖出订单
def sync_sell_filled_trade(client):
    all_orders = get_all_orders(client, 'EOSBTC');
    # 如果不为空
    if all_orders:
        for key,item in enumerate(all_orders):
            if("FILLED" == item['status']):
                print item
                b_id = item['clientOrderId']
                sell_order_id = item['orderId']
                sell_price = item['price']
                sell_qty = item['origQty']
                sell_time = item['time']
                update_btc_binance_trade(b_id, sell_order_id, sell_price, sell_qty, sell_time)

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_trade_sell()

    
    #is_sell_surplus, surplus_qty = get_sell_surplus('zhangchen', '', 2000.0)
    #print is_sell_surplus, surplus_qty

if __name__ == '__main__':
    main() 