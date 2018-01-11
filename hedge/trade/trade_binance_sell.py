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
from common_util import common_sync_all_order

def start_trade_sell():

    # 获取当前买入(还没有卖出的)的订单,准备卖出
    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])
        account = a_item['account']
        # 同步已经成交的卖出订单
        common_sync_all_order()
        
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
                orderId = item[3]


                curr_max_price = get_curr_max_price_klines(client)

                is_sell_record = False # 是否存在对应的卖出纪录, 没有则进入,有的话就跳过
                is_find_btc_binance_order_sell_record = find_btc_binance_order_sell_record(account, sellClientOrderId)
                if is_find_btc_binance_order_sell_record:
                    is_sell_record = True


                is_sell_surplus = False # 是否对应的卖出还有剩余, 有剩余则进入,没有的就跳过
                surplus_qty = 0.0 # 剩余数量
                is_sell_surplus, surplus_qty = get_sell_surplus(account, sellClientOrderId, executedQty)

                #print is_sell_surplus, surplus_qty

                sell_price, stop_sell_price = oper_stop_price(curr_max_price, buy_price)
                is_oper_sell = oper_is_sell(stop_sell_price, buy_price)


                # 买入的要卖出
                # 条件为: 
                # 1、必须有一定的利润
                if is_oper_sell:

                    # 2、状态为完成的
                    # 3、买卖类型为买
                    if(status == 'FILLED' and 'BUY' == side):
                        # 4、对应的卖出纪录不存在
                        if(not is_sell_record):
                            print "===================第一档==================="
                            print '当前最高价格: %s' % curr_max_price
                            print '买入订单ID: %s' % orderId
                            print '买入价格: %s ; 买入数量: %s' % (buy_price, executedQty)
                            print '触发价格: %s ; 止损价格: %s' % (sell_price, stop_sell_price)
                            set_stop_price_order(client, sell_price, stop_sell_price, executedQty, sellClientOrderId)

                        # 4、对应的卖出纪录存在, 但是数量不相等的
                        elif(is_sell_surplus):
                            print "===================第二档==================="
                            print '当前最高价格: %s' % curr_max_price
                            print '买入订单ID: %s' % orderId
                            print '买入价格: %s ; 买入数量: %s' % (buy_price, executedQty)
                            print '触发价格: %s ; 止损价格: %s' % (sell_price, stop_sell_price)
                            set_stop_price_order(client, sell_price, stop_sell_price, surplus_qty, sellClientOrderId)
                
                    # 2、状态为取消的
                    # 3、买卖类型为买
                    # 4、没有全部买入成功的(买成功部分)
                    if(status == 'CANCELED' and 'BUY' == side and origQty > executedQty and 0.0 != executedQty):
                        # 5、对应的卖出纪录不存在
                        if(not is_sell_record):
                            print "===================第三档==================="
                            print '当前最高价格: %s' % curr_max_price
                            print '买入订单ID: %s' % orderId
                            print '买入价格: %s ; 买入数量: %s' % (buy_price, executedQty)
                            print '触发价格: %s ; 止损价格: %s' % (sell_price, stop_sell_price)
                            set_stop_price_order(client, sell_price, stop_sell_price, executedQty, sellClientOrderId)
                        
                        # 5、对应的卖出纪录存在, 但是数量不相等的
                        elif(is_sell_surplus):
                            print "===================第四档==================="
                            print '当前最高价格: %s' % curr_max_price
                            print '买入订单ID: %s' % orderId
                            print '买入价格: %s ; 买入数量: %s' % (buy_price, executedQty)
                            print '触发价格: %s ; 止损价格: %s' % (sell_price, stop_sell_price)
                            set_stop_price_order(client, sell_price, stop_sell_price, surplus_qty, sellClientOrderId)

                # 买入的要卖出 (条件为: 状态为完成的、买卖类型为买、对应的卖出纪录存在, 但是数量不相等的)
                # if (is_oper_sell and status == 'FILLED' and 'BUY' == side):
                #     if(is_sell_surplus):
                #         print item, "02"


                # # 买入的部分要卖出 (条件为: 状态为取消的、买卖类型为买、对应的卖出纪录不存在)
                # if(status == 'CANCELED' and 'BUY' == side and origQty > executedQty and 0.0 != executedQty):
                #     if(not is_sell_record):
                #         print item, "03"

                # # 买入的部分要卖出 (条件为: 状态为取消的、买卖类型为买、对应的卖出纪录存在, 但是数量不相等的)
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


# 开始设置止损价格
def set_stop_price_order(client, sell_price, stop_sell_price, buy_qty, newClientOrderId):
    #return
    order_symbol = 'EOSBTC'
    order_side = SIDE_SELL
    order_type = ORDER_TYPE_TAKE_PROFIT_LIMIT
    order_timeInForce = TIME_IN_FORCE_GTC
    order_price = sell_price 
    order_stopPrice = stop_sell_price
    order_quantity = buy_qty
    #print order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newClientOrderId
    parentClientOrderId = newClientOrderId
    newClientOrderId = '%s%s%s' % (newClientOrderId,'66-66',str(int(time.time())))
    #检查是否和上一次设置的止损价格相同,如果相同,则不用取消重新设置; 如果不相同,则取消重新设置
    set_stop_record_result = find_btc_binance_order_stop_record(parentClientOrderId)
    if(set_stop_record_result):
        stopPrice = set_stop_record_result[8]
        price = set_stop_record_result[11]
        origQty = set_stop_record_result[3]
        orderId = set_stop_record_result[1]

        # 判断 触发价格、止损价格、购买数量是否相同; 如果相同,则不用取消重新设置; 如果不相同,则取消重新设置
        if( order_price == price and order_stopPrice == stopPrice and order_quantity == origQty):
            print "相同,不用设置"
        else:
            print "重新设置止损"
            cancel_order(client, order_symbol, orderId)
            sell_order_result = create_stop_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newClientOrderId )
            insert_btc_binance_order_stop_record(sell_order_result, parentClientOrderId)
    else:
        print "第一次设置"
        sell_order_result = create_stop_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newClientOrderId )
        insert_btc_binance_order_stop_record(sell_order_result, parentClientOrderId)


# 最高价格是否大于买入价格的2.5%
def oper_is_sell(stop_sell_price, buy_price):
    (stop_sell_price - buy_price)/buy_price

    sell_rate = (Decimal(stop_sell_price) - Decimal(buy_price))/Decimal(buy_price)
    sell_rate = round(sell_rate,8)
    if(sell_rate >= 0.025):
        return True
    
    return False

# 计算止损价格
def oper_stop_price(curr_max_price, buy_price):
    stop_rate = float(Decimal(1) - (Decimal(curr_max_price) - Decimal(buy_price))/Decimal(buy_price) * Decimal(0.05))
    stop_sell_price = round(float(curr_max_price) * stop_rate,8)
    sell_price = round(float(Decimal(stop_sell_price) * Decimal(1.0005)),8)
    return sell_price, stop_sell_price


# 获取买入交易对应的卖出交易,并获取剩余(没有卖出)的数量和纪录
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
    
# 获取当前的最高价格, 通过最近交易数据获取
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
    max_price = float(max_price) * float(1)
    return round(max_price,8)



# 获取当前的最高价格，通过K线数据获取
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

    max_price = float(max_price) * float(1)
    return round(max_price,8)


# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_trade_sell()

if __name__ == '__main__':
    main() 